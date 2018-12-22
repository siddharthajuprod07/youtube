#!/usr/bin/env python

import csv
import sys
import socket
import json
import requests as req

""" An adapter that takes CSV as input, performs a lookup to the operating
    system hostname resolution facilities, then returns the CSV results 

    This is intended as an example of creating external lookups in general.

    Note that the script offers mapping both ways, from host to IP and from IP
    to host.  
    
    Bidrectional mapping is always required when using an external lookup as an
    'automatic' lookup: one configured to be used without explicit reference in
    a search.

    In the other use mode, eg in a search string as "|lookup lookupname", it is
    sufficient to provide only the mappings that will be used.
"""

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

# Given an genrename, return the genreid
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

def main():
    if len(sys.argv) != 3:
        print "Usage: python tmdb_external_lookup.py [genre id] [genre name]"
        sys.exit(1)

    genreid = sys.argv[1]
    genrename = sys.argv[2]

    infile = sys.stdin
    outfile = sys.stdout

    r = csv.DictReader(infile)
    header = r.fieldnames

    w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
    w.writeheader()

    for result in r:
        # Perform the lookup or reverse lookup if necessary
        if result[genreid] and result[genrename]:
            # both fields were provided, just pass it along
            w.writerow(result)

        elif result[genreid]:
            # only genreid was provided, add genrename
            genrenames = lookup(result[genreid])
            for g in genrenames:
                result[genrename] = g["name"]
                w.writerow(result)

        elif result[genrename]:
            # only genrename was provided, add genreid
            genreids = rlookup(result[genrename])
            for gi in genreids:
                result[genreid] = gi["id"]
                w.writerow(result)

main()
