import requests as req
import sys, os
import json
import logging
import logging.handlers

def get_request_token(api_key):
    requestURL = "https://api.themoviedb.org/3/authentication/token/new"
    parameters = {"api_key":api_key}
    response=req.get(url=requestURL,params=parameters)
    data=response.json()
    request_token = data["request_token"]
    return request_token

def validate_with_login(api_key,request_token):
    requestURL = "https://api.themoviedb.org/3/authentication/token/validate_with_login"
    parameters = {"api_key":api_key}
    data = {"username":"siddhartha.juprod07","password": "s1ddh@rth@","request_token":request_token}
    response=req.post(url=requestURL,params=parameters,data=data)
    data=response.json()
    is_validated=data["success"]
    return is_validated

def get_session_id(api_key,request_token):
    requestURL = "https://api.themoviedb.org/3/authentication/session/new"
    parameters = {"api_key":api_key}
    data = {"request_token":request_token}
    response=req.post(url=requestURL,params=parameters,data=data)
    data=response.json()
    session_id = data["session_id"]
    return session_id

def create_list(api_key,session_id,list_name,list_desc,list_lang):
    requestURL = "https://api.themoviedb.org/3/list"
    parameters = {"api_key":api_key,"session_id":session_id}
    data = {"name":list_name,"description":list_desc,"language":list_lang}
    response=req.post(url=requestURL,params=parameters,data=data)
    data=response.json()
    list_id=data["list_id"]
    return list_id  

def add_movie_to_list(list_id,api_key,session_id,movie_id):
    requestURL = "https://api.themoviedb.org/3/list/" + str(list_id) + "/add_item"
    parameters = {"api_key":api_key,"session_id":session_id}
    data = {"media_id":movie_id}
    response=req.post(url=requestURL,params=parameters,data=data)
    data=response.json()
    return data
    

def setup_logger(level):
     logger = logging.getLogger('my_search_command')
     logger.propagate = False # Prevent the log messages from being duplicated in the python.log file
     logger.setLevel(level)
     file_handler = logging.handlers.RotatingFileHandler(os.environ['SPLUNK_HOME'] + '/var/log/splunk/tmdb_alert.log', maxBytes=25000000, backupCount=5)
     formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
     file_handler.setFormatter(formatter)
     logger.addHandler(file_handler)
     return logger
 
logger = setup_logger(logging.INFO)

    

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        payload = json.loads(sys.stdin.read())
        logger.info(payload)
        config = payload.get('configuration')
        api_key = config.get('APIkey')
        #is_create_list = config.get('cretlist')
        #list_desc = config.get('listdesc')
        list_id = config.get('listid')
        list_lang = config.get('listlang')
        event_result = payload.get('result')
        movie_id = event_result.get('id')
        request_token = get_request_token(api_key)
        is_validated = validate_with_login(api_key,str(request_token))
        if is_validated==True:
            session_id=get_session_id(api_key,request_token)
            logger.info(list_id)
            data = add_movie_to_list(list_id,api_key,session_id,movie_id)
            
    
    
if __name__ == "__main__":
    main()