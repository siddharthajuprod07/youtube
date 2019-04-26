class ApiConfig(object):
    
    host_and_port = None
    scheme = None
    
    @classmethod
    def splunkd_host_port(cls):
        if not cls.host_and_port:
            import splunk.clilib.cli_common as comm
            ipAndPort = comm.getWebConfKeyValue('mgmtHostPort')
            ip, port = ipAndPort.split(':')
            cls.host_and_port = (ip, int(port))
        return cls.host_and_port
        
    @classmethod
    def splunkd_scheme(cls):
        if not cls.scheme:
            import splunk.clilib.cli_common as comm
            import splunk.util as splutil
            enableSsl = comm.getConfKeyValue('server', 'sslConfig', 'enableSplunkdSSL')
            enableSsl = splutil.normalizeBoolean(enableSsl)
            cls.scheme = 'https' if enableSsl else 'http'
        return cls.scheme
        
