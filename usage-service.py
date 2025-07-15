import sys, json, csv, time, io
import utils as utils

from pathlib import Path

sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

def usage_service_mapping(filename, cur_path, env_name, bearer_token):

    url_dict = {
        "dev1":"dev.sys.cs.sgp.dbs.com",
        "dev2":"dev2.sys.cs.sgp.dbs.com",
        "uat3":"dev3.sys.tas.uat.dbs.com",
        "uat4":"dev4.sys.tas.uat.dbs.com",
        "sys1":"prod.sys1.cs.sgp.dbs.com",
        "sys2":"prod.sys2.cs.sgp.dbs.com"
    }

    headers={
        "Accept" : "application/json",
        "Authorization":"{}".format(bearer_token)
    }

    result={}
    with open(filename, 'r') as fh:
        for line in fh:
            org_object = (json.loads(line))
            org_guid = org_object["guid"]
            org_name = org_object["name"]
            
            print("Processing..{}".format(org_name))

            processes_base_url=url_dict.get(env_name)
            start_date = time.strftime("%Y-%m-01")
            today_date = time.strftime("%Y-%m-%d")
            url="https://app-usage.{0}/organizations/{1}/app_usages?start={2}&end={3}".format(processes_base_url,org_guid,start_date,today_date)
            print("url " + url)

            try:
                processes,response = utils.Common.make_request(url,headers)
            except:
                pass
            else:
                processes_str = processes.decode('utf-8')
                processes_json = json.loads(processes_str)

                app_usages = processes_json["app_usages"]
     
                for app_usage in app_usages:
                    app_guid = app_usage["app_guid"]
                    print(app_guid)
                    app_name = app_usage["app_name"]
                    space_name = app_usage["space_name"]
                    print(space_name)
                    instance_count = app_usage["instance_count"]
                    print(instance_count)
                    duration_in_seconds = app_usage["duration_in_seconds"]
                    print(duration_in_seconds)
      
                    key = org_guid +  "|" + app_guid + "|" + str(instance_count)
                    result[key] = {
                        'app_name' : app_name,
                        'space_name' : space_name,
                        'org_name': org_name,
                        'duration_in_seconds': duration_in_seconds
                    }

                    print(result)
            


    with open("{0}/{1}/app_usages_foundation.csv".format(cur_path,env_name), 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        fields= ['app name', 'app guid', 'space name', 'org name', 'org id', 'instance count', 'duration_in_seconds']
        writer.writerow(fields)
        
        for key, value in result.items():
            org_guid = key.split("|")[0]
            app_guid = key.split("|")[1]
            instance_count = key.split("|")[2]
            print("Processing...." + org_guid)
            data_list=[]

            data_list.append(value["app_name"])
            data_list.append(app_guid)
            data_list.append(value["space_name"])
            data_list.append(value["org_name"])
            data_list.append(org_guid)
            data_list.append(instance_count)
            data_list.append(value["duration_in_seconds"])
            writer.writerow(data_list)

if __name__ == "__main__":
    start_time = time.time()
    bearer_token=sys.argv[1]
    env_name=sys.argv[2]

    cur_path=Path(__file__).parent.absolute()
    usage_service_mapping("{0}/{1}/organizations.json".format(cur_path,env_name), cur_path, env_name, bearer_token)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Processing completed in {} seconds".format(elapsed_time))