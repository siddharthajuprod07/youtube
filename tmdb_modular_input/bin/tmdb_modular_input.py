
import sys,os
import requests as req
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.modularinput import *


class MyScript(Script):

    def get_scheme(self):
        # Returns scheme.
        scheme = Scheme("TMDB Modular Input")
        scheme.use_external_validation = False
        scheme.use_single_instance = False
        scheme.description = "TMDB Modular Input"

        api_key = Argument("api_key")
        api_key.title = "API Key"
        api_key.data_type = Argument.data_type_string
        api_key.description = "API Key"
        api_key.required_on_create = True
        api_key.required_on_edit = True
        scheme.add_argument(api_key)

        lang = Argument("lang")
        lang.title = "Language"
        lang.data_type = Argument.data_type_string
        lang.description = "Movie Language"
        lang.required_on_create = False
        lang.required_on_edit = False
        scheme.add_argument(lang)

        page_number = Argument("page_number")
        page_number.title = "Page Number"
        page_number.data_type = Argument.data_type_number
        page_number.description = "Page Number"
        page_number.required_on_create = False
        page_number.required_on_edit = False
        scheme.add_argument(page_number)

        region = Argument("region")
        region.title = "Region"
        region.data_type = Argument.data_type_string
        region.description = "Region"
        region.required_on_create = False
        region.required_on_edit = False
        scheme.add_argument(region)

        return scheme
    
    def tmdb_api_call(self,requestURL,parameters):
        response = req.get(url=requestURL,params=parameters)
        if response.status_code != 200:
            sys.exit(1)
        data = response.json()
        return data
    
    def get_upcoming_movies(self,api_key,page_num,lang,region):
        requestURL = "https://api.themoviedb.org/3/movie/upcoming"
        parameters = {"api_key":api_key,"page":page_num,"language":lang,"region":region}
        return self.tmdb_api_call(requestURL,parameters)


    def validate_input(self, validation_definition):
        # Validates input.
        pass

    def stream_events(self, inputs, ew):
        # Splunk Enterprise calls the modular input, 
        # streams XML describing the inputs to stdin,
        # and waits for XML on stdout describing events.
        # {"input_stanza1" : {"api_key": value, "lang": value...},"input_stanza2" : {"api_key": value, "lang": value...}}
        for input_name,input_item in inputs.inputs.items():
            api_key = input_item["api_key"]
            if "lang" in input_item:
                lang = input_item["lang"]
            else:
                lang = "en-US"

            if "page_number" in input_item:
                page_number = input_item["page_number"]
            else:
                page_number = 1

            if "region" in input_item:
                region = input_item["region"]
            else:
                region = ""
            
            result = self.get_upcoming_movies(api_key,page_number,lang,region)

            for r in result["results"]:
                event = Event()
                event.stanza = input_name
                event.data = json.dumps(r)
                ew.write_event(event)


if __name__ == "__main__":
    sys.exit(MyScript().run(sys.argv))