import os, sys
import json
import splunklib.client as client
from dbx2.dbx_logger import logger

class ShcClusterConfig(client.Entity):

    def __init__(self, service, **kwargs):
        kwargs.update({'skip_refresh': True})
        client.Entity.__init__(self, service, 'shcluster/config', **kwargs)

    def is_clustering_enabled(self):
        # DBX-1741 - don't check for clustering if we are not on enterprise
        is_enterprise = self._is_enterprise_product()
        if is_enterprise is False:
            return False
        mode = self.content['mode']
        enabled = is_enterprise and mode != 'disabled'
        logger.debug('action=retrieve_shc_clustering clustering_mode=%s clustering_enabled=%s', mode, enabled)
        return enabled

    def _is_enterprise_product(self):
        server_info = self.service.info()
        product_type = server_info['product_type']
        is_enterprise = product_type == 'enterprise'
        logger.debug('action=test_if_enterprise_product product_type=%s result=%s', product_type, is_enterprise)
        return is_enterprise




