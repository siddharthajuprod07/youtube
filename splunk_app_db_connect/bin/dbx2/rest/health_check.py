from __future__ import absolute_import
from dbx2.dbx_logger import logger

import splunk, os
from dbx2.simple_rest import SimpleRest
from dbx2.splunk_client.splunk_service_factory import SplunkServiceFactory
import splunklib.client as client
from dbx2.jre_validator import validateJRE
import requests
import platform
import subprocess


class Status:
    NOT_APPLICABLE = -1
    OK = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


# TODO: refactor health checker, split into different scripts
class HealthChecker(SimpleRest):
    splunk_home = os.environ.get('SPLUNK_HOME')

    path_to_app = os.path.join(splunk_home, 'etc', 'apps', 'splunk_app_db_connect')
    path_to_checkpoint = os.path.join(splunk_home, 'var', 'lib', 'splunk', "modinputs", "server",
                                      "splunk_app_db_connect")
    path_to_log = os.path.join(splunk_home, 'var', 'log', 'splunk')

    return_json = {
        "entry": {
            "content": {
                "severity_level": Status.NOT_APPLICABLE,
                "detail": ""
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super(HealthChecker, self).__init__(*args, **kwargs)
        self.check_dispatcher = {
            "java": self._check_java_installation_health,
            "java_server": self._check_java_server_configuration_health,
            "permission": self._check_file_permission_health,
            "driver": self._forward_request_to_proxy,
            "kerberos": self._forward_request_to_proxy,
            "inputs": self._forward_request_to_proxy,
            "outputs": self._forward_request_to_proxy,
            "lookups": self._forward_request_to_proxy,
            "connections": self._forward_request_to_proxy,
            "identities": self._forward_request_to_proxy
        }

    def illegalAction(self, verb):
        self.response.setStatus(405)
        self.addMessage('ERROR', 'HTTP %s not supported by the settings handler' % verb, 405)

    def handle_DELETE(self):
        self.illegalAction('DELETE')

    def handle_PUT(self):
        self.illegalAction('PUT')

    def handle_POST(self):
        self.illegalAction('POST')

    def handle_GET(self):
        try:
            item_to_check = self.pathParts[3]
            if not self.check_dispatcher.has_key(item_to_check):
                raise Exception("health check item is invalid, only the following items are supported: {}".format(
                    str(self.check_dispatcher.keys())))

            # get the mapped function and do the actual check job
            check_method = self.check_dispatcher[item_to_check]
            result = check_method()

            self.response.setHeader('content-type', 'application/json')

            if not isinstance(result, list):
                result = [result]

            self.return_json = {'entry': result}
            self.writeJson(self.return_json)
        except Exception as ex:
            self.response.setStatus(500)
            self.response.setHeader('content-type', 'application/json')
            self.return_json["entry"]["content"]["severity_level"] = Status.ERROR
            self.return_json["entry"]["content"]["details"] = str(ex)
            self.writeJson(self.return_json)

    def _check_java_installation_health(self):
        platform = self._detect_platform_dir()
        path_to_customized_java = os.path.join(self.path_to_app, platform, "bin", "customized.java.path")
        final_status = Status.OK
        final_details = []
        if not os.path.isfile(path_to_customized_java):
            # check if $JAVA_HOME/bin/java satisfies the requirement of JAVA 8 if JAVA_HOME is defined
            java_home = os.getenv("JAVA_HOME")
            if java_home:
                logger.debug("JAVA_HOME is {}".format(java_home))
                java_cmd = os.path.join(java_home, "bin", "java")
            else:
                logger.debug("JAVA_HOME is not specified.  Use default java command.")
                java_cmd = "java"

            # validating java command
            is_healthy, detail = validateJRE(java_cmd)
            if is_healthy:
                splunk_service = SplunkServiceFactory.create(self.sessionKey, app='splunk_app_db_connect',
                                                             owner=self.userName)
                result = self._check_commands(splunk_service)
                result.append(self._check_modular_alert_java_conf(splunk_service))

                # we reduce the results
                for status, details in result:
                    if status != Status.OK:
                        final_status = Status.ERROR
                        final_details.append(details)
            else:
                final_status = Status.ERROR
                final_details.append(detail)
        else:
            # check the content of customized.java.path
            with open(path_to_customized_java, 'r') as customized_java_file:
                java_cmd = customized_java_file.readline().strip()
                is_healthy, final_details = validateJRE(java_cmd)

                if not is_healthy:
                    final_status = Status.ERROR

        return self._create_health_check_result(final_status, final_details)

    def _check_java_server_configuration_health(self):
        # check if server.jar exists
        final_status = Status.OK
        final_details = []
        logger.info("check the existence of server.jar")
        path_to_server_jar = os.path.join(self.path_to_app, "jars", "server.jar")
        if not os.path.isfile(path_to_server_jar):
            detail = "{} does not exist".format(path_to_server_jar)
            final_status = Status.ERROR
            final_details.append(detail)
            return self._create_health_check_result(final_status, final_details)

        # check whether it can be successfully registered to Splunk
        logger.info("check whether the [server://default] modular input is registered successfully")
        input_url = "https://{}/services/data/modular-inputs/server".format(self.hostPath)
        try:
            response = requests.get(url=input_url, headers={'Authorization': ('Splunk %s' % self.sessionKey)},
                                    verify=False)
            if response.status_code != 200:
                final_status = Status.ERROR
                final_details.append("The modular input to start the Java Server failed to be registered to Splunk")
                return self._create_health_check_result(final_status, final_details)
        except Exception as ex:
            logger.error("action=fail_to_send_request_to_get_health_check_result", ex)
            final_status = Status.ERROR
            final_details.append("The modular input to start the Java Server failed to be registered to Splunk")
            return self._create_health_check_result(final_status, final_details)

        # check the availability of java server
        logger.debug("check the availability of java server")
        status, result = self._check_java_server_availability()
        if status != Status.OK:
            return self._create_health_check_result(status, result)

        return self._create_health_check_result(final_status, final_details)

    def _detect_platform_dir(self):
        system = platform.system().lower()
        architecture = platform.architecture()
        if system == "darwin":
            return system + "_x86_64"
        elif system in ("linux", "windows"):
            if "32bit" in architecture:
                return system + "_x86"
            else:
                return system + "_x86_64"
        else:
            raise Exception("this system is not supported by splunk")

    def _check_commands(self, splunk_service):
        checks = []
        # check commands.conf and alert_actions.conf's filename, should point to java.path
        commands_endpoint = "configs/conf-commands/{}"
        commands = ["dbxquery", "dbxoutput", "dbxlookup"]
        for command in commands:
            filename = client.Entity(splunk_service, commands_endpoint.format(command)).content["filename"]
            if filename != "java.path":
                current_command_check = (
                    Status.ERROR,
                    "{} command conf's filename property should be java.path, but it is: {} now.".format(command,
                                                                                                         filename))
            else:
                current_command_check = (Status.OK,
                                         'java path is correctly defined for {} command'.format(command))

            checks.append(current_command_check)

        return checks

    def _check_modular_alert_java_conf(self, splunk_service):
        alert_action_endpoint = "configs/conf-alert_actions/alert_output"
        alert_execute_cmd = client.Entity(splunk_service, alert_action_endpoint).content["alert.execute.cmd"]
        if alert_execute_cmd != "java.path":
            alert_execute_cmd_check = (Status.ERROR,
                                       "alert output conf's alert.execute.cmd property should be java.path, but it is: {} now.".format(
                                           alert_execute_cmd))
        else:
            alert_execute_cmd_check = (Status.OK,
                                       'java path is correctly defined for DB Connect modular alert')
        return alert_execute_cmd_check

    def _create_health_check_result(self, status, details):
        return {
            'content': {
                'severity_level': status,
                'details': details
            }
        }

    def _check_file_permission_health(self):
        unhealthy_folders = []
        paths_to_check_permission = [self.path_to_app, self.path_to_checkpoint, self.path_to_log]
        for path in paths_to_check_permission:
            # TODO: do we need to check sub dir permission?
            has_read_and_write_permission = (os.access(path, os.R_OK) and os.access(path, os.W_OK))
            logger.debug("file: {}, has read/write permission: {}".format(path, has_read_and_write_permission))
            if not has_read_and_write_permission:
                unhealthy_folders.append(path)

        if unhealthy_folders:
            status = Status.ERROR
            detail = "Following folder(s): {} don't exist or don't have read/write permissions".format(
                " ".join(unhealthy_folders))
        else:
            status = Status.OK
            detail = "All folders have appropriate permissions"

        return [self._create_health_check_result(status, [detail])]

    def _forward_request_to_proxy(self):
        status, result = self._check_java_server_availability()
        if status != Status.OK:
            return self._create_health_check_result(status, result)

        forward_url = "https://{}/servicesNS/{}/splunk_app_db_connect/{}/dbxproxy/{}" \
            .format(self.hostPath, self.userName, self.pathParts[1], "/".join(self.pathParts[2:]))
        try:
            response = requests.get(url=forward_url, headers={'Authorization': ('Splunk %s' % self.sessionKey)},
                                    verify=False)
            if response.status_code != 200:
                logger.warn(
                    "action=fail_to_send_request_to_get_health_check_result url={} status_code={} content={}".format(
                        forward_url, response.status_code, response.content))
                raise Exception(
                    "fail to get health check result from server url={} status_code={} content={}".format(forward_url,
                                                                                                          response.status_code,
                                                                                                          response.content))
            result = response.json()
            if isinstance(result, list):
                return [self._create_health_check_result(entry['severity_level'], entry['details']) for entry in result]
            else:
                return self._create_health_check_result(result['severity_level'], result['details'])

        except Exception as ex:
            logger.error("action=fail_to_send_request_to_get_health_check_result", ex)
            return "unhealthy", str(ex)

    def _check_java_server_availability(self):
        taskserver_status_url = "https://{}/servicesNS/{}/splunk_app_db_connect/db_connect/dbxproxy/taskserver" \
            .format(self.hostPath, self.userName)
        status = Status.OK
        detail = ''
        try:
            response = requests.get(url=taskserver_status_url,
                                    headers={'Authorization': ('Splunk %s' % self.sessionKey)},
                                    verify=False)
            if response.status_code != 200:
                logger.error(
                    "action=check_java_server_availability_failed error={}".format(taskserver_status_url,
                                                                                   response.content))
                status = Status.ERROR
                detail = response.content

        except Exception as ex:
            logger.error("action=check_java_server_availability_failed", ex)
            status = Status.ERROR
            detail = ex

        return status, detail

    def _execute(self, cmd):
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (result, error) = process.communicate()

        rc = process.wait()

        if rc != 0:
            logger.error("action=failed_to_execute_command:{} error={}".format(cmd, error))
        return rc, result
