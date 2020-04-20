
# encoding = utf-8

import os
import sys
import time
import datetime
import json

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # api_key = definition.parameters.get('api_key', None)
    pass

def collect_events(helper, ew):

    opt_api_key = helper.get_arg('api_key')
    url = 'https://api.themoviedb.org/3/movie/upcoming'
    page_number = 1
    parameters = {"api_key":opt_api_key,"page":page_number}
    final_result = []
    response = helper.send_http_request(url, 'GET', parameters=parameters, payload=None,
                                        headers=None, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=True)
    r_json = response.json()
    for movie in r_json["results"]:
        state = helper.get_check_point(str(movie["id"]))
        if state is None:
            final_result.append(movie)
            helper.save_check_point(str(movie["id"]), "Indexed")
        #helper.delete_check_point(str(movie["id"]))
    r_status=response.status_code
    if r_status !=200:
        response.raise_for_status()
    event = helper.new_event(json.dumps(final_result), time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
    ew.write_event(event)
