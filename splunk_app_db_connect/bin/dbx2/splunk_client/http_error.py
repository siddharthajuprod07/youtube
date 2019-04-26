import os, sys
import splunklib.binding as binding

def new_init(self, response, _message=None):
    """This exception is raised for HTTP responses that return an error.
    This monkey patched init method can handle json error too.
    """
    status = response.status
    reason = response.reason
    body = response.body.read()
    try:
        detail = XML(body).findtext("./messages/msg")
    except:
        detail = body
    message = "HTTP %d %s%s" % (
        status, reason, "" if detail is None else " -- %s" % detail)
    Exception.__init__(self, _message or message)
    self.status = status
    self.reason = reason
    self.headers = response.headers
    self.body = body
    self._response = response
    
binding.HTTPError.__init__ = new_init