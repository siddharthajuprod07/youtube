import splunklib.client as client
from splunklib.binding import HTTPError
from dbx2.dbx_logger import logger
import time
import urlparse
from dbx2.splunk_client.server_settings import ServerSettings

class ShcClusterCaptainInfo(client.Entity):

    def __init__(self, service, **kwargs):
        client.Entity.__init__(self, service, 'shcluster/captain/info', **{'skip_refresh': True})

    def is_captain(self, retryWait=2, maxRetries=6):
        retry = True
        step = 2
        retries = 0
        # exponential backoff because of SPL-90689
        while retry and retries < maxRetries:
            try:
                self.refresh()
                captain = self.content
                local_settings = ServerSettings(self.service)
                parsed_peer_scheme = urlparse.urlparse(captain['peer_scheme_host_port'])
                #dns comparisons are lowercase, https://tools.ietf.org/html/rfc4343
                local_server_name = local_settings['serverName'].lower()
                remote_server_name = captain['label'].lower()
                #until Ember we compare /server/settings/serverName vs shcluster/captain/info/label
                #and /server/settings/mgmtHostPort vs port in shcluster/captain/info/peer_scheme_host_port
                #for Ember, we have to use noProxy, see DBX-1774

                if local_server_name != remote_server_name:
                    logger.debug('action=not_shc_captain cause=server_name_unmatched local_name=%s remote_name=%s',
                                 local_server_name, remote_server_name)
                    return False

                local_server_port = int(local_settings['mgmtHostPort'])
                remote_server_port = int(parsed_peer_scheme.port)
                if local_server_port != remote_server_port:
                    logger.debug('action=not_shc_captain cause=port_unmatched local_port=%s remote_port=%s',
                                 local_server_port, remote_server_port)
                    return False
                return True
            except HTTPError as he:
                if he.status == 503:
                    retry = True
                    time.sleep(retryWait)
                    retryWait = retryWait * step
                    retries = retries + 1
                else:
                    return False
            
        logger.info('action=unable_to_determine_if_running_on_captain')
        return False

