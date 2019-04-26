import splunklib.client as client

class ServerSettings(client.Entity):

    def __init__(self, service, **kwargs):
        client.Entity.__init__(self, service, 'server/settings', **kwargs)

