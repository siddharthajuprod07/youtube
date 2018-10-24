import sys,os
import splunk.Intersplunk 
import json
import requests as req


def tmdb_api_call(requestURL,parameters):
    response=req.get(url=requestURL,params=parameters)
    if response.status_code !=200:
        print('Status: ',response.status_code,'Headers: ',response.headers,'Error Response: ',response.json())
        exit()
    data=response.json()
    return json.dumps(data)

def get_genre_dtl(genre_id):
    genres = []
    api_key = "733ac994290c6f277b11565f26ebe1cb"
    requestURL = "https://api.themoviedb.org/3/genre/movie/list"
    parameter = {"api_key" : api_key}
    genre_list = tmdb_api_call(requestURL,parameter)
    data = json.loads(genre_list)
    for genre in data["genres"]:
        if genre_id == "*":
            genres.append(genre)
        elif str(genre["id"]) == str(genre_id):
            genres.append(genre)
            break
    return genres

def process_events():
    results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
    for result in results:
        genreid = result["genre_id"]
        genre_dtls = get_genre_dtl(genreid)        
        result["genre name"] = genre_dtls[0]["name"]
    splunk.Intersplunk.outputResults(results) 

process_events()