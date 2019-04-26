import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import splunklib.client as client


class ConnectionTypes(client.Collection):
    PATH_CONNECTION_TYPES = 'db_connect/dbxproxy/connection_types'

    def __init__(self, service, **kwargs):
        client.Collection.__init__(self, service, ConnectionTypes.PATH_CONNECTION_TYPES)
