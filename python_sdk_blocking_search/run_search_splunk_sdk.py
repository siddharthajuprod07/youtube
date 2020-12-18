import splunklib.client as client
import splunklib.results as results


def connect_to_splunk(username,password,host='localhost',port='8089',owner='admin',app='search',sharing='user'):
    try:
        service = client.connect(host=host, port=port,username=username, password=password,owner=owner,app=app,sharing=sharing)
        if service:
            print("Splunk service created successfully")
            print("------------------------------------")
        return service
    except Exception as e:
        print(e)

def run_normal_mode_search(splunk_service,search_string,payload={}):
    try:
        job = splunk_service.jobs.create(search_string,**payload)
        #print(job.content)
        while True:
            while not job.is_ready():
                pass
            if job["isDone"] == "1":
                break
        for result in results.ResultsReader(job.results()):
            print(result)

    except Exception as e:
        print(e)

def run_blocking_mode_search(splunk_service,search_string,payload={}):
    try:
        job = splunk_service.jobs.create(search_string,**payload)
        print(job.content)
        for result in results.ResultsReader(job.results()):
            print(result)

    except Exception as e:
        print(e)


def main():
    try:
        splunk_service = connect_to_splunk(username='admin',password='test1234')
        search_string= "search index=tmdb_index | table id,original_language,original_title"
        #payload = {"exec_mode":"normal"}
        payload = {"exec_mode":"blocking"}
        #run_normal_mode_search(splunk_service,search_string,payload)
        run_blocking_mode_search(splunk_service,search_string,payload)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()

