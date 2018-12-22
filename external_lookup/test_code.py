# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import json
import requests as req

def tmdb_api_call(requestURL,parameters):
    response=req.get(url=requestURL,params=parameters)
    if response.status_code !=200:
        print('Status: ',response.status_code,'Headers: ',response.headers,'Error Response: ',response.json())
        exit()
    data=response.json()
    return json.dumps(data)

# Given a genreid, find the genrename
def lookup(genreid):
    try:
        genres = []
        api_key = "733ac994290c6f277b11565f26ebe1cb"
        requestURL = "https://api.themoviedb.org/3/genre/movie/list"
        parameter = {"api_key" : api_key}
        genre_list = tmdb_api_call(requestURL,parameter)
        data = json.loads(genre_list)
        for genre in data["genres"]:
            if genreid == "*":
                genres.append(genre)
            elif str(genre["id"]) == str(genreid):
                genres.append(genre)
                break
        return genres
    except:
        return []

def rlookup(genrename):
    try:
        genres = []
        api_key = "733ac994290c6f277b11565f26ebe1cb"
        requestURL = "https://api.themoviedb.org/3/genre/movie/list"
        parameter = {"api_key" : api_key}
        genre_list = tmdb_api_call(requestURL,parameter)
        data = json.loads(genre_list)
        for genre in data["genres"]:
            if genrename == "*":
                genres.append(genre)
            elif str(genre["name"]) == str(genrename):
                genres.append(genre)
                break
        return genres
    except:
        return []

#genres = lookup("16")
genres = rlookup("Animation")
for g in genres:
    print(g["id"])
