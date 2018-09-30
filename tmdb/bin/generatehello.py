import sys, time
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

@Configuration()
class GenerateHelloCommand(GeneratingCommand):
    count = Option(require=True, validate=validators.Integer())

    def generate(self):
        for i in range(1, self.count + 1):
            text = 'Hello World %d' % i
            yield {'_time': time.time(), 'event_no': i, '_raw': text }

dispatch(GenerateHelloCommand, sys.argv, sys.stdin, sys.stdout, __name__)