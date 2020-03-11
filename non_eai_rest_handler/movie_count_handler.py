import os
import sys
import splunklib.client as client
import splunklib.results as results
import logging
import logging.handlers
import json

from splunk.persistconn.application import PersistentServerConnectionApplication

def setup_logger(level):
     logger = logging.getLogger('custom_rest')
     logger.propagate = False # Prevent the log messages from being duplicated in the python.log file
     logger.setLevel(level)
     file_handler = logging.handlers.RotatingFileHandler(os.environ['SPLUNK_HOME'] + '/var/log/splunk/movie_count_handler.log', maxBytes=25000000, backupCount=5)
     formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
     file_handler.setFormatter(formatter)
     logger.addHandler(file_handler)
     return logger
 
logger = setup_logger(logging.INFO)




class MovieCountHandler(PersistentServerConnectionApplication):
    def __init__(self, command_line, command_arg):
        PersistentServerConnectionApplication.__init__(self)
    
    def parse_query_parameter(self,query_parameter):
        qury_param_dict = {}
        for p in query_parameter:
            qury_param_dict[p[0]] = p[1]
        logger.info(qury_param_dict)
        return qury_param_dict

    def handle(self, in_string):
        try:
            logger.info(in_string)
            in_string_json = json.loads(in_string)
            session_key= in_string_json["session"]["authtoken"]
            query_parameter = in_string_json["query"]
            method = in_string_json["method"]
            logger.info("session_key : {} , query_parameter: {}, method : {}".format(session_key,query_parameter,method))
            qury_param_dict = self.parse_query_parameter(query_parameter)
            if method == "GET":
                service = client.connect(host='localhost',port=8089,app='tmdb',token=session_key)
                searchquery = 'search index=tmdb_index original_language=' + str(qury_param_dict['ln']) + ' | stats count'
                kwargs_query = {"earliest_time": "0","latest_time": "now"}
                search_results = service.jobs.oneshot(searchquery, **kwargs_query)
                reader = results.ResultsReader(search_results)
                for item in reader:
                    logger.info(item["count"])
                    payload_val = item["count"]
                status = 200
            if method == "POST":
                form_parameter = in_string_json["form"]
                logger.info("form_parameter : {}".format(form_parameter))
                payload_val = "Currently POST not supported"
                status = 200
            return {'payload': str(payload_val),'status': status}
        except Exception as e:
            logger.info(e)