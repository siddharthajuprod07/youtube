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


def main():
    try:
        splunk_service = connect_to_splunk(username='admin',password='test1234')
        savedsearches = savedsearch_list(splunk_service)
        name="new_saved_search"
        search = "index=_internal|stats count by sourcetype"
        payload_ss = '''{
                    "cron_schedule":"*/2 * * * *",
                    "description":"This is a saved search",
                    "is_scheduled": "1",
                    "disabled":"0",
                    "dispatch.earliest_time": "-1d",
                    "dispatch.latest_time": "now"}
        '''
        create_savedsearch(savedsearches,name,search,json.loads(payload_ss))
        savedsearch_list(splunk_service)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()