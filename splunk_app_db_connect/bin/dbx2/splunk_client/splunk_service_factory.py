import ssl
import urlparse
import splunklib.client as client
from splunklib.binding import handler
from api_config import ApiConfig
import os
from dbx2.dbx_logger import logger


class SplunkServiceFactory(object):
    @classmethod
    def create(cls, session_key=None, app=None, owner=None, sharing=None, server_url=None):
        if server_url is None:  # try provide url, this branch is cpu intensive
            scheme = ApiConfig.splunkd_scheme()
            host = ApiConfig.splunkd_host_port()[0]
            port = ApiConfig.splunkd_host_port()[1]
        else:
            if isinstance(server_url, basestring):
                server_url = urlparse.urlparse(server_url)
            scheme = server_url.scheme
            host = server_url.hostname
            port = server_url.port

        custom_handler = cls._create_handler()

        service = client.connect(scheme=scheme, host=host, port=port,
                                 token=session_key, app=app, owner=owner, sharing=sharing, handler=custom_handler)

        return service

    @classmethod
    def _create_handler(cls):
        script_dir = os.path.dirname(os.path.realpath(__file__))

        key_file_location = os.path.join(script_dir, '..', '..', '..', 'certs', 'privkey.pem')
        cert_file_location = os.path.join(script_dir, '..', '..', '..', 'certs', 'cert.pem')

        key_file_exists = os.path.isfile(key_file_location)
        cert_file_exists = os.path.isfile(cert_file_location)

        if key_file_exists and cert_file_exists:
            logger.debug('action=enable_client_certicates')
        else:
            key_file_location = cert_file_location = None
            if key_file_exists != cert_file_exists:
                logger.warn(
                    'Unable to enable client certificate because the key or the certificate is missing.' \
                    'certs application folder should contain privkey.pem and cert.pem files')

        custom_handler = handler(key_file=key_file_location, cert_file=cert_file_location)

        # we wrap the handler to intercept any SSL exception to give a meaningful message to end user
        def handler_wrapper(url, message, **kwargs):
            logger.debug('action=sending_request url=%s message=%s kwargs=%s', url, message, kwargs)
            try:
                return custom_handler(url, message, **kwargs)
            except ssl.SSLError:
                message = 'Unable to communicate with Splunkd. ' \
                          'If you enable requireClientCert please make sure certs folder contains privkey.pem and cert.pem files. ' \
                          'Also make sure cert.pem has been signed by the root CA used by Splunkd.'
                logger.error(message, exc_info=True)
                raise ssl.SSLError(message)

        return handler_wrapper
