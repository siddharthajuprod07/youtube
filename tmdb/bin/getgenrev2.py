#!/usr/bin/env python

import sys,time
import requests as req
import json
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators

@Configuration()
class getgenrev2Command(GeneratingCommand):
    """ %(synopsis)

    ##Syntax

    %(syntax)

    ##Description

    %(description)

    """
    genreid = Option(require=True)
    def tmdb_api_call(self,requestURL,parameters):
        response=req.get(url=requestURL,params=parameters)
        if response.status_code !=200:
            print('Status: ',response.status_code,'Headers: ',response.headers,'Error Response: ',response.json())
            exit()
        data=response.json()
        return json.dumps(data)

    def get_genre_dtl(self):
        api_key = "733ac994290c6f277b11565f26ebe1cb"
        requestURL = "https://api.themoviedb.org/3/genre/movie/list"
        parameter = {"api_key" : api_key}
        genre_list = self.tmdb_api_call(requestURL,parameter)
        data = json.loads(genre_list)
        return data
    
    def generate(self):
       # Put your event  code here
       genres_list = []
       genres = self.get_genre_dtl()
       for genre in genres["genres"]:
           if self.genreid == "*":
               genres_list.append(genre)
           elif str(genre["id"]) == str(self.genreid):
               genres_list.append(genre)
       for outputgenre in genres_list:
           yield{"_time": time.time(),"id" : outputgenre["id"],"name" : outputgenre["name"]}

dispatch(getgenrev2Command, sys.argv, sys.stdin, sys.stdout, __name__)