# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 13:00:33 2019

@author: siddh
"""

import splunklib.client as client

service = client.connect(host='localhost',port=8089,app='tmdb',username='admin',password='changeme')

kwargs_email = {'action.email.to':'sid@gmail.com'}

my_saved_searches = service.saved_searches.list()

for search in my_saved_searches:
    print(search.name)
    #search.enable()
    search.update(**kwargs_email)