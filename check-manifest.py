## pip3 install pyyaml
## python3 check-manifest.py ./spring-music-cds_manifest.yml

import sys, json, csv, time, io
import subprocess
import yaml 
import requests

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

def check_manifest_services(manifest, cf_services):
    # print ("cf_services:"+str(cf_services))
    print("Checking Service instance from the manifest: "+manifest)
    print("  Current service instances in this space:"+ str(cf_services))
    try:
        f=open(manifest,'r')
    except IOError:
        print ("file not found:"+ manifest)
        sys.exit()


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
                

def check_routes(manifest):
    print("Checking Routes from the manifest: "+manifest)
    try:
        f=open(manifest,'r')
    except IOError:
        print ("file not found:"+ manifest)
        sys.exit()

    occupied=[]
    with f:
        manifestYaml = yaml.safe_load(f)
        for application in manifestYaml["applications"]:
            appName=application["name"]
            if not "routes" in application:
              continue
            routes=application["routes"]
            for routeDict in routes:
                route=routeDict["route"]
                try:
                  response = requests.get("https://"+route, timeout=1)
                except:
                    continue
                if response== None:
                    continue
                # print ("res:"+ str(response.status_code))
                if response.status_code==200:
                   occupied.append("  Route '{0}' under application '{1}' responding with http-code 200".format(route, appName))

    f.close()
    if not occupied:
        print ("  All routes from the manifest MAYBE available")
        return True
    else:
        print ("  Found Routes that might be used already:")
        for instance in occupied:
            print ("  - {0}".format(instance))
        return False
        

if __name__ == "__main__":
    start_time = time.time()

    all_good=True
    manifest=sys.argv[1]
    print_cf_target()
    cf_services= fetch_cf_services()
    all_good=check_manifest_services(manifest, cf_services)
    all_good=check_routes(manifest)
    end_time = time.time()
    elapsed_time = end_time - start_time
    # print("Processing completed in {} seconds".format(elapsed_time))
    
    if not all_good:
        sys.exit(1)
        

