import dbx_bootstrap_env
import splunk.Intersplunk as interSplunk
from dbx2.splunk_client.splunk_service_factory import SplunkServiceFactory
import splunklib.client as client

# get data volume per source type
results, dummy_results, settings = interSplunk.getOrganizedResults()

splunk_service = SplunkServiceFactory.create(session_key=settings['sessionKey'],
                                             app=settings['namespace'],
                                             owner=settings['owner'])

all_inputs = client.Collection(splunk_service, 'configs/conf-db_inputs').list()

# get all source types.
source_types = set([x.content.get('sourcetype') for x in all_inputs
                    if 'splunk_app_db_connect' == x.content.get('eai:appName')])

# get data volume per source type.
output = [x for x in results if x.get('series') in source_types]

# return result
interSplunk.outputResults(output)
