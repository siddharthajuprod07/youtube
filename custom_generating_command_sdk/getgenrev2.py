from __future__ import absolute_import, division, print_function, unicode_literals
import os,sys
import time
import json
import requests as req
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators



@Configuration(type="reporting")
class getgenrev2(GeneratingCommand):

    
    genreid = Option(require=True)

    def tmdb_api_call(self,requestURL,parameters):
        response=req.get(url=requestURL,params=parameters)
        if response.status_code !=200:
            print('Status: ',response.status_code,'Headers: ',response.headers,'Error Response: ',response.json())
            exit()
        data=response.json()
        return json.dumps(data)

    def get_genre_dtl(self,genre_id):
        genres = []
        api_key = "733ac994290c6f277b11565f26ebe1cb"
        requestURL = "https://api.themoviedb.org/3/genre/movie/list"
        parameter = {"api_key" : api_key}
        genre_list = self.tmdb_api_call(requestURL,parameter)
        data = json.loads(genre_list)
        for genre in data["genres"]:
            if genre_id == "*":
                genres.append(genre)
            elif str(genre["id"]) == str(genre_id):
                genres.append(genre)
        return genres

    def generate(self):
        genre_list = self.get_genre_dtl(self.genreid)
        for outputgenre in genre_list:
            yield {'_time': time.time(),'id' : outputgenre["id"], 'name' : outputgenre["name"], '_raw': str(outputgenre["id"]) + "," + str(outputgenre["name"])}

dispatch(getgenrev2, sys.argv, sys.stdin, sys.stdout, __name__)