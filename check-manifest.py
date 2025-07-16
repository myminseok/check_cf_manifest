## pip3 install pyyaml
## python3 check-manifest.py ./spring-music-cds_manifest.yml

import sys, json, csv, time, io
import subprocess
import yaml 

def print_cf_target():
    p = subprocess.Popen('cf target', shell=True)
    retval = p.wait()
    if retval:
      sys.exit(1)

def fetch_cf_services():
    p = subprocess.Popen('cf curl /v3/service_instances | jq \'.resources[].name\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cf_services=[]
    for line in p.stdout.readlines():
        line=line.strip() ## remove starting,ending whitespaces
        line=line[1:-1] ## remove starting,ending double quote
        line=line.decode('utf-8') ## convert byte to str
        cf_services.append(line)
    retval = p.wait()
    if retval:
      sys.exit(1)
    return  cf_services

def check_manifest_services(manifest):
    print("Checking Service instance from the manifest ({0})".format(manifest))
    try:
        f=open(manifest,'r')
    except IOError:
        print ("file not found:"+ manifest)
        sys.exit()

    cf_services= fetch_cf_services()
    print("  Current service instances in this space '{0}'".format(str(cf_services)))
    missing=[]
    with f:
        manifestYaml = yaml.safe_load(f)
        for application in manifestYaml["applications"]:
            appName=application["name"]
            services=application["services"]
            for service in services:
                if service in cf_services:
                    pass
                else:
                    missing.append("  Missing '{0}' under application '{1}'".format(service, appName))
    f.close()
    if not missing:
        print ("  All service instance from the manifest exists in current space")
        return True
    else:
        print ("  Found Missing service instance:")
        for instance in missing:
            print ("  - {0}".format(instance))
        return False
                
## https://v3-apidocs.cloudfoundry.org/version/3.197.0/index.html#check-reserved-routes-for-a-domain
## fetch domain list/guid
## fetch routes from manifest.yml



def fetch_cf_domains():
    print("Fetching cf domains from the target foundation ...")
    p = subprocess.Popen('cf curl /v3/domains | jq \'.resources[]| "\(.name) \(.guid)"\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cf_domains_dict=dict()
    for line in p.stdout.readlines():
        line=line.strip() ## remove starting,ending whitespaces
        line=line[1:-1] ## remove starting,ending double quote
        line=line.decode('utf-8') ## convert byte to str
        keyval=line.split()
        cf_domains_dict[keyval[0]]=keyval[1]
        
    retval = p.wait()
    # print(cf_domains_dict)
    return cf_domains_dict


## if route domain not match -> wrong.
def check_route_domain_match(manifestRoute, cf_domains_dict):
    manifestRouteSplit=manifestRoute.split('.',1)
    # print(manifestRouteSplit)
    if len(manifestRouteSplit) < 2:
        return False, "Invalid route domain. too short '{0}'".format(manifestRoute)
    manifestDomain=manifestRouteSplit[1]
    if manifestDomain in cf_domains_dict.keys():
        return True, "Matching route domain in cf domains"
    else:
        return False, "No such domain '{0}' in cf domains".format(manifestDomain)
    


## if route reserved -> wrong.
def check_cf_domain_reserved(manifestRoute, cf_domains_dict):
    manifestRouteSplit=manifestRoute.split('.',1)
    # print(manifestRouteSplit)
    if len(manifestRouteSplit) < 2:
        return False, "Invalid route domain '{0}'".format(manifestRoute)
    domainGuid=cf_domains_dict.get(manifestRouteSplit[1])

    url="curl -H \"Authorization: $(cf oauth-token)\" https://api.sys.dhaka.cf-app.com/v3/domains/{0}/route_reservations\?host\={1}".format(domainGuid,manifestRouteSplit[0])
    # print (url)
    p = subprocess.Popen(url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cf_domains_dict=dict()
    ## "matching_route":true
    response=""
    for line in p.stdout.readlines():
        line=line.strip() ## remove starting,ending whitespaces
        line=line[1:-1] ## remove starting,ending double quote
        line=line.decode('utf-8') ## convert byte to str
        if "matching_route" in line:
            # print(line)
            if line.split(":")[1] == "true":
                return True
            else:
                return False
    retval = p.wait()
    
def check_routes(manifest):
    print("Checking Routes availability from the manifest ({0})".format(manifest))
    try:
        f=open(manifest,'r')
    except IOError:
        print ("file not found:"+ manifest)
        sys.exit()

    cf_domains_dict= fetch_cf_domains()
    occupied=[]
    with f:
        manifestYaml = yaml.safe_load(f)
        for application in manifestYaml["applications"]:
            appName=application["name"]
            if not "routes" in application:
              continue
            manifestRoutes=application["routes"]
            for routeDict in manifestRoutes:
                manifestRoute=routeDict["route"]
                match, err= check_route_domain_match(manifestRoute, cf_domains_dict)
                if not match:
                     occupied.append("  {0} ('{1}' under application '{2}')".format(err, manifestRoute, appName))
                if check_cf_domain_reserved(manifestRoute, cf_domains_dict):
                     occupied.append("  Route is reserved ('{0}' under application '{1}')".format(manifestRoute, appName))

    f.close()
    if not occupied:
        print ("  All routes from the manifest available")
        return True
    else:
        print ("  Found Routes Not Available:")
        for instance in occupied:
            print ("  - {0}".format(instance))
        return False
        

if __name__ == "__main__":
    start_time = time.time()

    all_good=True
    manifest=sys.argv[1]
    print_cf_target()

    print("")
    all_good=check_routes(manifest)

    print("")
    all_good=check_manifest_services(manifest)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    # print("Processing completed in {} seconds".format(elapsed_time))
    
    if not all_good:
        sys.exit(1)
        

