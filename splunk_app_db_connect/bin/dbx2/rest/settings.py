from __future__ import absolute_import
from dbx2.dbx_logger import logger

import splunk, os, json
from json import loads
import requests

import splunklib.client as client

from dbx2 import get_app_path
from dbx2.simple_rest import SimpleRest
from dbx2.java_home_detector import JavaHomeDetector
from dbx2.splunk_client.splunk_service_factory import SplunkServiceFactory
from dbx2 import jvm_options
from dbx2.jre_validator import validateJRE, checkDependencies


class Settings(SimpleRest):
    endpoint = "configs/conf-dbx_settings/java"
    defaultPort = 9998

    commands_endpoint = "configs/conf-commands/%s"
    java_commands = ["dbxquery", "dbxoutput", "dbxlookup"]
    customized_java_path = "customized.java.path"

    taskserverPortProperty = "dw.server.applicationConnectors[0].port"
    taskserverPortRegex = r'dw\.server\.applicationConnectors\[0\]\.port=(\d+)'

    restart_url = "http://127.0.0.1:%s/api/taskserver"

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
            self.check_java_home(content)
            self.read_vmopts(content)
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
            pre_taskserverport = self.read_taskserver_port()
            payload = loads(self.request['payload'])
            self.check_java_home(payload)
            # check whether the javaHome is valid
            self.validate_java_home(payload["javaHome"])
            self.update_vmopts(payload)
            splunk_service = SplunkServiceFactory.create(self.sessionKey, app='splunk_app_db_connect',
                                                 owner=self.userName)
            entity = client.Entity(splunk_service, self.endpoint)
            entity.update(**payload).refresh()
            logger.debug('updated java settings')
            self.update_dbx_java_home(payload["javaHome"])
            self.reset_java_command_filename(splunk_service)
            self.read_vmopts(entity.content)
            self.restart_task_server(pre_taskserverport)
            self.writeJson(entity.content)
        except Exception as ex:
            self.response.setStatus(500)
            self.writeJson({
                "code": 500,
                "message": ex.message,
                "detail": str(ex)
            })

    def check_java_home(self, content):
        if "javaHome" not in content:
            if "JAVA_HOME" in os.environ:
                java_home = os.environ["JAVA_HOME"].replace('"', '')
                content["javaHome"] = java_home
            else:
                try:
                    java_home = JavaHomeDetector.detect()
                    content["javaHome"] = java_home
                except Exception as ex:
                    logger.warn("java home auto detection failed")
                    content["javaHome"] = ""

    # DBX-3248 write java home to specific file so that it can be used to start server and java search command.
    def update_dbx_java_home(self, javaHome):
        app_dir = get_app_path()

        java_path_darwin = os.path.join(app_dir, "darwin_x86_64", "bin", self.customized_java_path)
        java_path_linux32 = os.path.join(app_dir, "linux_x86", "bin", self.customized_java_path)
        java_path_linux64 = os.path.join(app_dir, "linux_x86_64", "bin", self.customized_java_path)
        java_path_win32 = os.path.join(app_dir, "windows_x86", "bin", self.customized_java_path)
        java_path_win64 = os.path.join(app_dir, "windows_x86_64", "bin", self.customized_java_path)

        java_home_files = [
            {"filename": java_path_darwin, "suffix": "/bin/java"},
            {"filename": java_path_linux32, "suffix": "/bin/java"},
            {"filename": java_path_linux64, "suffix": "/bin/java"},
            {"filename": java_path_win32, "suffix": "\\bin\\java.exe"},
            {"filename": java_path_win64, "suffix": "\\bin\\java.exe"}
        ]
        for java_home_file in java_home_files:
            try:
                with open(java_home_file["filename"], "w") as file:
                    file.write(javaHome + java_home_file["suffix"])
                    logger.info('update java path file [%s]' % java_home_file["filename"])
            except IOError as er:
                logger.error('unable to update java path file [%s]' % java_home_file["filename"])
                raise

    def reset_java_command_filename(self, splunk_service):
        for java_command in self.java_commands:
            entity = client.Entity(splunk_service, self.commands_endpoint % java_command)
            # If customer have set the filename to "customized.java.path", we need to reset it to "java.path"
            # Related issue: DBX-3746
            if entity["filename"] == self.customized_java_path:
                entity.update(filename="java.path").refresh()
                logger.debug("action=reset_java_command_filename command=%s" % java_command)

    def read_vmopts(self, content):
        content['jvmOptions'] = ''
        content['taskServerPort'] = self.defaultPort
        try:
            jvmopts = jvm_options.read()
            content['jvmOptions'] = jvmopts
            taskServerPort = jvm_options.get_property(jvmopts, self.taskserverPortProperty, self.taskserverPortRegex)
            if taskServerPort:
                content['taskServerPort'] = int(taskServerPort)
        except Exception as ex:
            logger.error('unable to read vmopts file [%s]' % ex)
            raise

    def update_vmopts(self, content):
        try:
            jvmopts = content.pop('jvmOptions', '') # jvmOptions may contain taskServerPort settings
            taskServerPort = content.pop('taskServerPort', self.defaultPort)
            logger.debug('action=get_vmopts_from_postdata, jvmOptions: [%s], taskServerPort: [%s]'
                         % (jvmopts, taskServerPort))
            if not isinstance(taskServerPort, int):
                raise Exception("task server port must be a int value")
            if taskServerPort < 1024 or taskServerPort > 65535:
                raise Exception('task server port must be a number in [1024, 65535]')
            jvmopts = jvm_options.set_property(jvmopts, self.taskserverPortProperty, self.taskserverPortRegex, str(taskServerPort))
            jvm_options.write(jvmopts)
        except Exception as ex:
            logger.error('unable to update vmopts file [%s]' % ex)
            raise

    def validate_java_home(self, java_home):
        if os.path.isdir(java_home):
            java_cmd = os.path.join(java_home, "bin", "java")
            is_valid, reason = validateJRE(java_cmd)
            if is_valid:
                is_valid, reason = checkDependencies(java_home)

            if not is_valid:
                raise Exception(reason)
        else:
            raise Exception("JAVA_HOME path not exist")

    @classmethod
    def read_taskserver_port(cls):
        try:
            jvmopts = jvm_options.read()
            taskServerPort = jvm_options.get_property(jvmopts, cls.taskserverPortProperty, cls.taskserverPortRegex)
            if taskServerPort:
                return taskServerPort
            else:
                return cls.defaultPort
        except Exception as ex:
            logger.error('unable to read vmopts file, use default port 8080, error info: [%s]' % ex)
            return cls.defaultPort

    def restart_task_server(self, taskserver_port):
        try:
            # settings update successfully, then trigger restart server api to make change taking effect
            requests.delete(self.restart_url % taskserver_port, verify=False)
        except Exception as ex:
            # if task server is not running, this request will failed
            logger.warn("action=restart_task_server_request_failed", ex)
