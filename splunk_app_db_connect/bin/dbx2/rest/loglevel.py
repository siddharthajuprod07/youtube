from __future__ import absolute_import
from dbx2.dbx_logger import logger

import splunklib.client as client
import requests

from json import loads, dumps
from dbx2.simple_rest import SimpleRest
from dbx2.splunk_client.splunk_service_factory import SplunkServiceFactory

from dbx2 import jvm_options
from dbx_rh_settings import Settings


class LogLevelHandler(SimpleRest):
    taskserverPort = Settings.read_taskserver_port()
    server_log_level_url = "http://127.0.0.1:" + str(taskserverPort) + "/api/loglevel"

    endpoint = "configs/conf-dbx_settings/loglevel"
    command_level_args = ["dbxquery", "dbxoutput", "dbxlookup"]
    server_level_args = ["dbinput", "dboutput", "connector"]
    allowed_levels = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR"]

    # WARNING: packages field is used to change the log level of server module in runtime.
    # If server package structure changed, you should also update the packages field
    # according to the new package structure. Or the logging level setting function for
    # server will not take effect if you don't restart the server.
    server_module_info = {
        "dbinput": {
            "property" : "DBINPUT_LOG_LEVEL",
            "regex": r'DBINPUT_LOG_LEVEL=\w+',
            "packages" : ["com.splunk.dbx.server.dbinput"],
        },
        "dboutput": {
            "property" : "DBOUTPUT_LOG_LEVEL",
            "regex": r'DBOUTPUT_LOG_LEVEL=\w+',
            "packages" : ["com.splunk.dbx.server.dboutput", "com.splunk.dbx.service.output"]
        },
        "connector": {
            "property" : "CONNECTOR_LOG_LEVEL",
            "regex": r'CONNECTOR_LOG_LEVEL=\w+',
            "packages" : ["com.splunk.dbx.connector"]
        }
    }

    def illegalAction(self, verb):
        self.response.setStatus(405)
        self.addMessage('ERROR', 'HTTP %s not supported by the settings handler' % verb, 405)

    def handle_DELETE(self):
        self.illegalAction('DELETE')

    def handle_PUT(self):
        self.handle_POST(self)

    def handle_PATCH(self):
        self.handle_POST(self)

    def handle_GET(self):
        try:
            splunk_service = SplunkServiceFactory.create(self.sessionKey, app='splunk_app_db_connect',
                                                         owner=self.userName)
            content = client.Entity(splunk_service, self.endpoint).content
            self.writeJson(content)
        except Exception as ex:
            self.response.setStatus(500)
            self.writeJson({
                "code": 500,
                "message": ex.message,
                "detail": str(ex)
            })


    def handle_POST(self):
        try:
            payload = loads(self.request['payload'])
            splunk_service = SplunkServiceFactory.create(self.sessionKey, app='splunk_app_db_connect',
                                                 owner=self.userName)
            entity = client.Entity(splunk_service, self.endpoint)
            # first update file first
            self.update_log_level(payload, splunk_service)
            # update the entity in conf file
            entity.update(**payload).refresh()
            self.writeJson(entity.content)
        except Exception as ex:
            self.response.setStatus(500)
            self.writeJson({
                "code": 500,
                "message": ex.message,
                "detail": str(ex)
            })

    def update_log_level(self, content, splunk_service):
        server_log_level = {}
        for (module, level) in content.items():
            if not level in self.allowed_levels:
                raise Exception("%s is not a valid log level" % level)
            if module in self.command_level_args:
                self._update_command_log_level(module, level, splunk_service)
            elif module in self.server_level_args:
                # collect server side module first, then update
                server_log_level[module] = level;
            else:
                raise Exception("%s is not a valid log module" % module)
        self._update_server_log_level(server_log_level);

    def _update_command_log_level(self, module, log_level, splunk_service):
        logger.debug("action=try_to_update_command_log_level module=%s, level=%s" % (module, log_level))
        command_endpoint = "configs/conf-commands/%s"
        # use this property to configure log level
        log_level_property = "-DDBX_COMMAND_LOG_LEVEL="

        entity = client.Entity(splunk_service, command_endpoint % module)
        to_update = {key : value for key,  value in entity.content.items() if log_level_property in value}
        if len(to_update) != 1:
            raise Exception("%s stanza in commands conf file is not valid because there must exist"
                            " one and only one attribute with a value -DDBX_COMMAND_LOG_LEVEL=${LOG_LEVEL}", module);
        log_args = to_update.keys()[0]
        log_level_value = to_update[log_args]
        original_log_level = log_level_value.split(log_level_property)[1]
        if original_log_level != log_level:
            logger.debug("action=update_command_log_level module=%s, original_level=%s level=%s" % (module, original_log_level, log_level))
            to_update[log_args] = log_level_property + log_level
            entity.update(**to_update).refresh()

    def _update_server_log_level(self, server_log_level):
        # update log level in vmopts file
        self._update_server_log_level_in_file(server_log_level)
        # send api to server, make the change take effect
        self._update_server_log_level_runtime(server_log_level)

    def _update_server_log_level_in_file(self, server_log_level):
        logger.debug("action=try_to_update_server_log_level %s" % str(server_log_level))
        try:
            jvmopts = jvm_options.read()
            logger.debug("action=read_vmopts_from_file vmopts=%s" % jvmopts)
            for (module, level) in server_log_level.items():
                property = self.server_module_info[module]["property"]
                regex = self.server_module_info[module]["regex"]
                jvmopts = jvm_options.set_property(jvmopts, property, regex, level)
            jvm_options.write(jvmopts)
        except Exception as ex:
            logger.error('unable to update vmopts file [%s]' % ex)
            raise

    def _update_server_log_level_runtime(self, server_log_level):
        data = []
        for (module, level) in server_log_level.items():
            packages = self.server_module_info[module]["packages"]
            for package in packages:
                data.append({
                    "logger": package,
                    "level": level
                })
        try:
            logger.debug("action=send_log_level_update_request url=%s data=%s" % (self.server_log_level_url, dumps(data)))
            headers = {
                'content-type': 'application/json'
            }
            response = requests.put(url=self.server_log_level_url, headers=headers, data=dumps(data), verify=False)
            if response.status_code != 200:
                logger.warn("acton=fail_to_send_request_to_update_log_level status=%s content=%s" % (response.status_code, response.content))
        except Exception as ex:
            # TODO: whether to raise error? vmopts file have been updated successfully
            logger.warn("acton=fail_to_send_request_to_update_log_level", ex)
