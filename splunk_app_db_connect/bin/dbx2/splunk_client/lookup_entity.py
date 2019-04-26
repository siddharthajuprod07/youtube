import os, sys
import json
import splunklib.client as client

PATH_LOOKUP_PATH = 'db_connect/dbxproxy/lookups/%s'


class LookupEntity(client.Entity):
    def __init__(self, service, name, **kwargs):
        path = PATH_LOOKUP_PATH % name
        client.Entity.__init__(self, service, path, **kwargs)


