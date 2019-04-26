import splunklib.client as client
from splunklib.binding import _encode

PATH_CONNECTION_PATH = 'db_connect/dbxproxy/connections/%s'


class ConnectionEntity(client.Entity):
    def __init__(self, service, name, **kwargs):
        path = PATH_CONNECTION_PATH % name
        client.Entity.__init__(self, service, path, **kwargs)

    def move(self, move_args):
        body = _encode(**move_args)
        return self.post('move', **{'body': body})
