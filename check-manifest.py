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

def check_manifest_services(manifest, cf_services):
    # print ("cf_services:"+str(cf_services))
    print("Checking Service instance from manifest: "+manifest)
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
    if not missing:
        print ("  All service instance from the manifest exists in current space")
    else:
        print ("  Found Missing service instance:")
        for instance in missing:
            print ("  - {0}".format(instance))
                

        


if __name__ == "__main__":
    start_time = time.time()

    manifest=sys.argv[1]
    print_cf_target()
    cf_services= fetch_cf_services()
    check_manifest_services(manifest, cf_services)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    # print("Processing completed in {} seconds".format(elapsed_time))