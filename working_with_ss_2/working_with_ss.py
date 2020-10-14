import splunklib.client as client
import json



def connect_to_splunk(username,password,host='localhost',port='8089',owner='admin',app='search',sharing='user'):
    try:
        service = client.connect(username=username,password=password,host=host,port=port,owner=owner,app=app,sharing=sharing)
        if service:
            print("Splunk service created successfully")
            print("-----------------------------------")
    except Exception as e:
        print(e)
    return service

def savedsearch_list(splunk_service):
    try:
        savedsearches= None
        if splunk_service:
            savedsearches = splunk_service.saved_searches
            for ss in savedsearches:
                print(ss.name)
        print("-----------------------------------")
    except Exception as e:
        print(e)
    return savedsearches

def create_savedsearch(savedsearch_collection,name,search,payload={}):
    try:
        if savedsearch_collection:
            mysearch = savedsearch_collection.create(name,search,**payload)
            if mysearch:
                print("{} object created successfully".format(mysearch.name))
                print("-----------------------------------")
    except Exception as e:
        print(e)

def update_savedsearch(splunk_service,savedsearch_name,new_search,new_payload={}):
    try:
        mysavedsearch = splunk_service.saved_searches[savedsearch_name]
        print(mysavedsearch.content)
        current_search = mysavedsearch["search"]
        if new_search:
            updated_search = new_search
        else:
            updated_search = current_search
        mysavedsearch.update(updated_search,**new_payload).refresh()
        print(mysavedsearch["search"])
        print("-----------------------------------")
    except Exception as e:
        print(e)
    print("{} updated correctly".format(savedsearch_name))

def delete_savedsearch(splunk_service,savedsearch_name):
    try:
        splunk_service.saved_searches.delete(savedsearch_name)
    except Exception as e:
        print(e)
    print("{} deleted correctly".format(savedsearch_name))


def main():
    try:
        splunk_service = connect_to_splunk(username='admin',password='test1234')
        savedsearches = savedsearch_list(splunk_service)
        #name="new_saved_search"
        name = "new_alert"
        search = "index=_internal|stats count by sourcetype"
        payload_ss = '''{
                    "cron_schedule":"*/2 * * * *",
                    "description":"This is a saved search",
                    "is_scheduled": "1",
                    "disabled":"0",
                    "dispatch.earliest_time": "-1d",
                    "dispatch.latest_time": "now"}
        '''
        payload_alert = '''{
                    "cron_schedule":"*/2 * * * *",
                    "description":"This is a sample  alert",
                    "is_scheduled": "1",
                    "disabled":"0",
                    "dispatch.earliest_time": "-1d",
                    "dispatch.latest_time": "now",
                    "actions":"email",
                    "action.email.to":"techiesid1985@gmail.com",
                    "alert.digest_mode":"1",
                    "alert_type":"number of events",
                    "alert_comparator":"greater than",
                    "alert_threshold":"0"}
        '''
        #create_savedsearch(savedsearches,name,search,json.loads(payload_alert))
        #savedsearch_list(splunk_service)
        new_search = "index=_internal|stats count by source"
        new_payload = {"cron_schedule":"*/20 * * * *","description":"This is a updated alert"}
        #update_savedsearch(splunk_service,name,new_search,new_payload)
        delete_savedsearch(splunk_service,name)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()