import sys,os
import json
import requests as req
import splunk.entity as entity
import logging
import logging.handlers

def setup_logger(level):
     logger = logging.getLogger('tmdb_upcoming')
     logger.propagate = False # Prevent the log messages from being duplicated in the python.log file
     logger.setLevel(level)
     file_handler = logging.handlers.RotatingFileHandler(os.environ['SPLUNK_HOME'] + '/var/log/splunk/tmdb_upcoming.log', maxBytes=25000000, backupCount=5)
     formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
     file_handler.setFormatter(formatter)
     logger.addHandler(file_handler)
     return logger
 
logger = setup_logger(logging.INFO)

def getCredentials(sessionKey):
    myapp = 'tmdb'
    logger.info(myapp)
    try:
        entities = entity.getEntities(['admin', 'passwords'], namespace=myapp,owner='nobody', sessionKey=sessionKey)
        #logger.info(entities)
    except Exception as e:
        raise Exception("Could not get %s credentials from splunk. Error: %s" % (myapp, str(e)))
    for i, c in entities.items():
        logger.info(c['username'])
        if c['username'] == "Sid":
            logger.info(c['clear_password'])
            return c['clear_password']
        raise Exception("No credentials have been found")  

def tmdb_api_call(requestURL,parameters):
    response=req.get(url=requestURL,params=parameters)
    if response.status_code !=200:
        print('Status: ',response.status_code,'Headers: ',response.headers,'Error Response: ',response.json())
        exit()
    data=response.json()
    return json.dumps(data)

def get_upcoming_movies_by_page(api_key,page_number=1):
    requestURL = "https://api.themoviedb.org/3/movie/upcoming"
    #requestURL = "https://api.tmdb.org/3/movie/upcoming" #users in India please use this line of code for your requests
    parameters = {"api_key":api_key,"page":page_number}
    return tmdb_api_call(requestURL,parameters)

def get_upcoming_movie_full_list(api_key):
    results_fetched = True
    page_number = 1
    final_list = []
    while results_fetched:
        upcoming_movies = get_upcoming_movies_by_page(api_key,page_number)
        data = json.loads(upcoming_movies)
        final_list.append(data["results"])
        results_fetched = bool(data["results"])
        page_number += 1
    return final_list

def is_empty(file_path):
    return os.stat(file_path).st_size==0

def checkpoint(checkpoint_file,movie_id):
    with open(checkpoint_file,'r') as file:
        id_list = file.read().splitlines()
        return (movie_id in id_list)

def write_to_checkpoint_file(checkpoint_file,data):
    with open(checkpoint_file,'a') as file:
        file.writelines(data + "\n")


def stream_to_splunk(checkpoint_file,data):
    if checkpoint(checkpoint_file,str(data["id"])):
        exit()
    else:
        write_to_checkpoint_file(checkpoint_file,str(data["id"]))
        print(json.dumps(data))

def main():
    sessionKey = sys.stdin.readline().strip()
    logger.info(sessionKey)
    if len(sessionKey) == 0:
        logger.error("Did not receive a session key from splunkd.Please enable passAuth in inputs.conf")
        exit(2)
    api_key = getCredentials(sessionKey)
    #api_key='733ac994290c6f277b11565f26ebe1cb'
    checkpoint_file = os.path.join(os.environ["SPLUNK_HOME"],'etc','apps','tmdb','bin','checkpoint','checkpoint.txt')
    upcoming_movie_list = get_upcoming_movie_full_list(api_key)
    for movie_list_by_page in upcoming_movie_list:
        for movie in movie_list_by_page:
            #data = json.dumps(movie)
            stream_to_splunk(checkpoint_file,movie)

if __name__ == "__main__":
    main()
