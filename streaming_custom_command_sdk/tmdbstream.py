#!/usr/bin/env python

import sys
import requests as req
from splunklib.searchcommands import \
    dispatch, StreamingCommand, Configuration, Option, validators


@Configuration()
class getgenrestreamCommand(StreamingCommand):
    """ %(synopsis)

    ##Syntax

    %(syntax)

    ##Description

    %(description)

    """
    fieldname = Option(
        doc='''
        **Syntax:** **fieldname=***<fieldname>*
        **Description:** Name of the field that will hold the genre name''',
        require=True, validate=validators.Fieldname())

    def stream(self, events):
       # Put your event transformation code here
       api_key = "733ac994290c6f277b11565f26ebe1cb"
       requestURL = "https://api.themoviedb.org/3/genre/movie/list"
       parameter = {"api_key" : api_key}
       response=req.get(url=requestURL,params=parameter)
       data=response.json()
       genre_dict = {}
       for d in data["genres"]:
           genre_dict[str(d["id"])] = str(d["name"])
       for event in events:
           genre_id = event["genre_ids"]
           event[self.fieldname] = genre_dict[str(genre_id)]
           yield event

dispatch(getgenrestreamCommand, sys.argv, sys.stdin, sys.stdout, __name__)
