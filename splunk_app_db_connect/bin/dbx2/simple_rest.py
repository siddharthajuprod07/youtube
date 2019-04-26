import json
import splunk.rest

from dbx_logger import logger

class SimpleRest(splunk.rest.BaseRestHandler):
    @property
    def userName(self):
        return self.request["userName"]

    @property
    def hostPath(self):
        return self.request["headers"]["host"]

    @property
    def host(self):
        return self.hostPath.split(":")[0]

    def writeJson(self, data):
        self.response.write(json.dumps(data))
