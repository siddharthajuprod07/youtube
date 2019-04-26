#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import dbx_bootstrap_env
import argparse
import collections
import json
import os.path
import shutil
import sys
import urlparse
import errno
import re
import datetime
import subprocess
import getpass
import urllib
import splunklib.client as client

script_dir, _ = os.path.split(os.path.abspath(sys.argv[0]))

usage_message = """
The migration script is to help you to upgrade to DB Connect 3.0.0. If you are running V2.3.0, V2.3.1 or V2.4.0 of
DB Connect, you can use this script to upgrade. If your DB Connect version is not listed here, please refer to the
documentation on how to migrate.

If there is a JDBC driver that depends on other libraries (i.e., ojdbc7 depends on xmlparser.jar), the migration script
will not be able to migrate all dependencies. Please refer the documentation for instructions on completing these
driver migrations manually.
"""

splunk_home = os.path.join(script_dir, "..", "..", "..", "..")
db_connect_home = os.path.join(script_dir, "..")


DB_CONNECT_APP_NAME = "splunk_app_db_connect"

Action = collections.namedtuple("Action", ['description', 'action'])
actions = list()

running_on_deployer = False
CONNECTIONS_WHITE_LIST_3_0 = ["serviceClass", "customizedJdbcUrl", "jdbcUseSSL", "jdbcDriverClass", "testQuery",
                              "database", "connection_type", "identity", "isolation_level", "readonly", "host",
                              "port", "informixserver", "useConnectionPool", "connection_properties", "fetch_size",
                              "maxConnLifetimeMillis", "maxWaitMillis", "maxTotalConn"]

CONNECTION_TYPES_WHITE_LIST_3_0 = ["serviceClass", "supportedVersions", "jdbcUrlFormat", "jdbcUrlSSLFormat", "jdbcUseSSL",
                                   "jdbcDriverClass", "testQuery", "displayName", "database", "port", "useConnectionPool",
                                   "ui_default_catalog", "ui_default_schema", "maxConnLifetimeMillis", "maxWaitMillis",
                                   "maxTotalConn", "connection_properties"]

INPUTS_SERVER_WHITE_LIST_3_0 = ["config_file", "keystore_password", "interval", "disabled"]

DB_INPUTS_WHITE_LIST_3_0 = ["description", "interval", "index", "source", "sourcetype", "host", "mode", "connection",
                            "query", "query_timeout", "max_rows", "fetch_size", "batch_upload_size", "tail_rising_column_name",
                            "tail_rising_column_fullname", "tail_rising_column_number", "input_timestamp_column_name",
                            "input_timestamp_column_fullname", "input_timestamp_column_number", "input_timestamp_format",
                            "max_single_checkpoint_file_size", "ui_query_mode", "ui_query_catalog", "ui_query_schema",
                            "ui_query_table", "disabled", "interval"]

DB_OUTPUTS_WHITE_LIST_3_0 = ["description", "interval", "connection", "table_name", "using_upsert", "unique_key",
                             "query_timeout", "search", "is_saved_search", "time_out", "customized_mappings",
                             "ui_mappings", "ui_selected_fields", "ui_saved_search_str", "ui_query_sql", "ui_query_mode",
                             "ui_query_catalog", "ui_query_schema", "ui_query_table", "disabled", "interval"]

DB_LOOKUPS_WHITE_LIST_3_0 = ["description", "lookupSQL", "connection", "input_fields", "output_fields", "ui_query_mode",
                             "ui_query_catalog", "ui_query_schema", "ui_query_table", "ui_input_spl_search",
                             "ui_input_saved_search", "ui_use_saved_search", "ui_query_result_columns",
                             "ui_column_output_map", "ui_field_column_map", "disabled"]

verbose_logging = False


def _quit_with_description(description, code=-1):
    eprint(description)
    if code != 0:
        eprint("abort!")
    sys.exit(code)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def _mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

black_list = ["antlr4-annotations-4.4.jar", "avro-compiler-1.7.6.jar", "dbx2.jar", "jetty-http-9.2.4.v20141103.jar",
              "jetty-server-9.2.4.v20141103.jar", "log4j-1.2.17.jar",  "slf4j-api-1.7.7.jar", "antlr4-runtime-4.4.jar",
              "avro-ipc-1.7.6.jar", "jetty-io-9.2.4.v20141103.jar", "jetty-servlet-9.2.4.v20141103.jar",
              "rpcserver-all.jar", "slf4j-log4j12-1.7.7.jar", "avro-1.7.6.jar", "commons-logging-1.1.2.jar",
              "jackson-all-1.9.11.jar", "jetty-security-9.2.4.v20141103.jar", "jetty-util-9.2.4.v20141103.jar",
              "servlet-api-3.1.jar"]


def check_drivers_to_be_migrated():
    try:
        old_dir = os.path.join(db_connect_home, "bin", "lib")
        new_dir = os.path.join(db_connect_home, "drivers")

        def migrate():
            if os.path.exists(new_dir):
                shutil.rmtree(new_dir)  # make copytree happy
            shutil.copytree(old_dir, new_dir, symlinks=True, ignore=shutil.ignore_patterns(*black_list))

        if os.path.isdir(old_dir):
            description = "move jdbc drivers to new location {}".format(new_dir)
            actions.append(Action(description, migrate))
        else:
            eprint("%s does not exist, driver migration will be skipped" % old_dir)
    except Exception as ex:
        eprint("failed to migrate jdbc drivers, cause:%s" % str(ex))


def _backup_file(from_file, to_dir):
    print("backup file {} to directory {}".format(from_file, to_dir))

    if not os.path.exists(to_dir):
        _mkdir_p(to_dir)
    shutil.copy2(from_file, to_dir)


def _copy_dir(from_dir, to_dir):
    print("backup directory {} to location {}".format(from_dir, to_dir))
    shutil.copytree(from_dir, to_dir, symlinks=True)


def check_file_to_be_backuped(apps):
    print("scan configuration files to be backup ...")

    backup_dir = os.path.join(db_connect_home, "migration_backups")

    if os.path.exists(backup_dir):
        if _yes_or_no("looks like there is already a previous backup, would you like remove it and backup again? [Y/n]"):
            shutil.rmtree(backup_dir)
        else:
            if _yes_or_no("backup will be skipped, do you want to continue? [Y/n]"):
                return
            else:
                _quit_with_description("abort!")

    from_dir = os.path.join(db_connect_home, "local")
    to_dir = os.path.join(backup_dir, DB_CONNECT_APP_NAME,  "local")

    if os.path.isdir(from_dir):
        _copy_dir(from_dir, to_dir)
    else:
        eprint("Cannot find any DB Connect local configurations to backup")

    from_dir = os.path.join(db_connect_home, "certs")
    to_dir = os.path.join(backup_dir, DB_CONNECT_APP_NAME, "certs")

    if os.path.isdir(from_dir):
        _copy_dir(from_dir, to_dir)
    else:
        _quit_with_description("Cannot find certificates to back up, corrupted installation?")

    conf_to_be_check = ["db_connections.conf", "db_connection_types.conf", "inputs.conf"]

    for app in apps:
        if app == DB_CONNECT_APP_NAME:  # already backup-ed
            continue
        else:
            for conf in conf_to_be_check:
                from_file = os.path.join(splunk_home, "etc", "apps", app, "local", conf)
                to_dir = os.path.join(backup_dir, app, "local")
                if os.path.exists(from_file):
                    _backup_file(from_file, to_dir)


# sdk has a bug then we write our own
def _is_key_exist(entity, key):
    try:
        entity[key]
        return True
    except:
        return False


def _is_input_exist(entity, name, kind):
    try:
        entity[name, kind]
        return True
    except:
        return False


def _normalize_boolean(val):
    return True if val in ['1', 'true', 't', 'yes'] else False


def _get_stanza_full_name(stanza):
    name = stanza.name
    if hasattr(stanza, "kind"):
        name = stanza.kind + "://" + name
    return name


def _add_update_operation(conf_name, stanza, to_update):
    description = "update {}, stanza {}\n".format(conf_name, _get_stanza_full_name(stanza))

    for key, value in to_update.iteritems():
        description += "\t{}={}\n".format(key, value)

    actions.append(Action(description, lambda: stanza.update(**to_update)))


def _add_enable_disable_stanza_operation(conf_name, stanza, enable=True):
    description = "{} stanza in conf {}".format("enable" if enable else "disable", conf_name)

    def do_enable_disable():
        if enable:
            stanza.enable()
        else:
            stanza.disable()

    actions.append(Action(description, do_enable_disable))

same_name_checker = set()


def _add_create_stanza_action(service, conf_name, title, properties, acl):
    if (conf_name, title) in same_name_checker:
        eprint("you have duplicate stanza names in {}.conf! {}".format(conf_name, title))
        eprint("Please rename one of them and then restart the migration!")
        _quit_with_description("duplicated stanza name detected", -1)
    else:
        same_name_checker.add((conf_name, title))

        description = "app[{}] create stanza {} in {}.conf with properties:\n".format(service.namespace.app, title, conf_name)
        for key, value in properties.iteritems():
            description += "\t{}={}\n".format(key, value)

        def create_stanza():
            new_stanza = service.confs[conf_name].create(title, **properties)
            if acl is not None:
                _update_stanza_acl(new_stanza, acl)

        actions.append(Action(description, create_stanza))


def _add_write_file_operation(path, content, mode="w"):
    description = "write file {} with content: {}".format(path, content)

    def write_file_operation():
        with open(path, mode) as f:
            f.write(content)

    actions.append(Action(description, write_file_operation))


def check_db_connections_conf(service, service_with_dbx_ns):
    conf_name = "db_connections.conf"

    if "db_connections" not in service.confs:
        return

    to_delete_properties = ['cwallet_location', 'sslConnectionType', 'oracle_cipher_suites',
                            'jdbcUrlFormat', 'jdbcUrlSSLFormat', 'enable_query_wrapping']

    db_connections_conf = service.confs['db_connections']
    for connection in db_connections_conf:
        if connection.access['app'] != service.namespace.app:
            if verbose_logging:
                print("connection {} belongs to app {}, current app {}, skip...".
                      format(connection.name, connection.access['app'], service.namespace.app))
            continue

        if not _check_stanza_acl(connection):
            eprint("db_connections.conf stanza {} in app {}, cannot be migrated because of permission settings, "
                   "sharing:{}".format(connection.name, connection.access['app'], connection.access['sharing']))
            continue

        connection_type_name = connection['connection_type']
        identity_name = connection['identity']

        if not _is_key_exist(connection, "connection_properties"):
            if _is_key_exist(connection, 'cwallet_location') and _is_key_exist(connection, 'oracle_cipher_suites'):
                connection_properties = {
                    # HACK: There's no way for python to tell if the Oracle connection is one-way or two-way. So here
                    # we just copy it to both trustStore & keyStore.
                    'javax.net.ssl.trustStore': connection['cwallet_location'],
                    'javax.net.ssl.keyStore': connection['cwallet_location'],
                    'javax.net.ssl.trustStoreType': "SSO",
                    'javax.net.ssl.keyStoreType': "SSO",
                    'oracle.net.authentication_services': "(TCPS)",
                    'oracle.net.ssl_cipher_suites': connection['oracle_cipher_suites']
                }

                to_update = {
                    'connection_properties': json.dumps(connection_properties)
                }

                _add_update_operation(conf_name, connection, to_update)
            elif _is_key_exist(connection, 'cwallet_location') or _is_key_exist(connection, 'oracle_cipher_suites'):
                eprint("WARN: connection %s is misformatted, please check cwallet_location and "
                       "oracle_cipher_suites, make sure all of them exist" % connection.name)

        if 'db_connection_types' in service.confs and connection_type_name in service.confs['db_connection_types']:
            connection_type = service.confs['db_connection_types'][connection_type_name]
        elif 'db_connection_types' in service_with_dbx_ns.confs \
                and connection_type_name in service_with_dbx_ns.confs['db_connection_types']:
            connection_type = service_with_dbx_ns.confs['db_connection_types'][connection_type_name]
        else:
            connection_type = None
            eprint("Cannot find connection_type definition, connection pool settings will be skipped")

        if 'identities' in service.confs and identity_name in service.confs['identities']:
            identity = service.confs['identities'][identity_name]
        elif 'identities' in service_with_dbx_ns.confs \
                and identity_name in service_with_dbx_ns.confs['identities']:
            identity = service_with_dbx_ns.confs['identities'][identity_name]
        else:
            identity = None
            eprint("Cannot find identity definition, this may cause errors during migration")

        if connection_type is not None:
            for item in ['maxConnLifetimeMillis', 'maxWaitMillis', 'maxTotalConn']:
                if _is_key_exist(connection_type, item):
                    to_update = {
                        item: connection_type[item]
                    }
                    _add_update_operation(conf_name, connection, to_update)

            use_ssl = False
            if _is_key_exist(connection, "jdbcUseSSL"):
                use_ssl = _normalize_boolean(connection['jdbcUseSSL'])
            elif _is_key_exist(connection_type, "jdbcUseSSL"):
                use_ssl = _normalize_boolean(connection_type["jdbcUseSSL"])

            is_customized = _is_key_exist(connection, "jdbcUrlFormat") or _is_key_exist(connection, "jdbcUrlSSLFormat")

            properties = dict(connection_type.content)
            properties.update(connection.content)
            if identity is not None:
                properties.update(identity.content)
            else:
                eprint("connection {} defined without corresponding identity, probably corrupt conf".format(connection.name))

            if is_customized:
                url_template = properties['jdbcUrlFormat'] if not use_ssl else properties['jdbcUrlSSLFormat']
                jdbc_url = _replace_token(url_template, properties)
                _add_update_operation(conf_name, connection, {"customizedJdbcUrl": jdbc_url})

        _check_properties_to_remove(db_connections_conf, connection, to_delete_properties)


def _replace_token(source, lookup_table):
    source = re.sub(r"<(\w+?)>", r"{\1}", source)
    return source.format(**lookup_table)


def _check_properties_to_remove(confs, stanza, to_delete_properties):
    to_delete = []
    for property in to_delete_properties:
        if _is_key_exist(stanza, property):
            to_delete.append(property)
    if len(to_delete) > 0:
        _add_remove_stanza_property_action(confs, stanza, to_delete)


def _add_remove_stanza_property_action(confs, stanza, to_delete_properties):
    description = "delete deprecated properties [{}] from conf file {}".format(",".join(to_delete_properties), confs.name)

    def remove_properties():
        s = confs[stanza.name]
        s.refresh()

        properties = dict(s.content)
        for property in to_delete_properties:
            if property in properties:
                properties.pop(property)

        s.delete()
        new_stanza = confs.create(s.name, **properties)
        _update_stanza_acl(new_stanza, s.access)

    actions.append(Action(description, remove_properties))


def _update_stanza_acl(stanza, acl):
    try:
        prop = {
            "sharing": acl.sharing,
            "owner": acl.app,
            "perms.read": ",".join(acl.perms.read),
            "perms.write": ",".join(acl.perms.write)
        }
        stanza.post("acl", body=urllib.urlencode(prop))
    except:
        eprint("update acl for stanza {} failed.".format(stanza.name))


def _add_remove_stanza_action(conf_name, stanza):
    description = "app[{}] delete stanza {} from {}".format(stanza.service.namespace.app, stanza.name, conf_name)

    def delete_stanza():
        stanza.delete()

    actions.append(Action(description, delete_stanza))


def check_db_connection_types_conf(service):
    conf_name = "db_connection_types.conf"

    if "db_connection_types" not in service.confs:
        return

    to_delete_properties = ['cwallet_location', 'sslConnectionType', 'oracle_cipher_suites', 'supportedMajorVersion', 'supportedMinorVersion']

    db_connection_types_conf = service.confs['db_connection_types']

    for connection_type in service.confs['db_connection_types']:
        if connection_type.access['app'] != service.namespace.app:
            if verbose_logging:
                print("connection type {} belongs to app {}, current app {}, skip...".
                      format(connection_type.name, connection_type.access['app'], service.namespace.app))
            continue

        if not _check_stanza_acl(connection_type):
            eprint("db_connection_types.conf stanza {} in app {} cannot be migrated because of permission settings, "
                   "sharing:{}".format(connection_type.name, connection_type.access['app'],
                                               connection_type.access['sharing']))
            continue

        if not _is_key_exist(connection_type, "connection_properties"):
            if _is_key_exist(connection_type, 'cwallet_location') and _is_key_exist(connection_type, 'oracle_cipher_suites'):
                connection_properties = {
                    'oracle.net.wallet_location': connection_type['cwallet_location'],
                    'oracle.net.authentication_services': "(TCPS)",
                    'oracle.net.ssl_cipher_suites': connection_type['oracle_cipher_suites']
                }
                to_update = {
                    'connection_properties': json.dumps(connection_properties)
                }
                _add_update_operation(conf_name, connection_type, to_update)
            elif _is_key_exist(connection_type, 'cwallet_location') or _is_key_exist(connection_type, 'oracle_cipher_suites'):
                eprint("connection type %s is malformated, please check cwallet_location and "
                       "oracle_cipher_suites, make sure all of them is correct" % connection_type.name)

        if _is_key_exist(connection_type, 'supportedVersions'):
            if _is_key_exist(connection_type, 'supportedMajorVersion'):
                if _is_key_exist(connection_type, 'supportedMinorVersion'):
                    minor_version = connection_type['supportedMinorVersion']
                else:
                    minor_version = '0'
                supported_versions = ".".join([connection_type['supportedMajorVersion'], minor_version])

                to_update = {
                    'supportedVersions': supported_versions
                }

                _add_update_operation(conf_name, connection_type, to_update)
            elif _is_key_exist(connection_type, 'supportedMinorVersion'):
                eprint("connection type %s is malformated, please check field about "
                             "supportedMajorVersion or supportedMinorVersion" % connection_type.name)

        _check_properties_to_remove(db_connection_types_conf, connection_type, to_delete_properties)


def _update_java_home(service, java_home):
    java_path_darwin = os.path.join(db_connect_home, "darwin_x86_64", "bin", "customized.java.path")
    java_path_linux32 = os.path.join(db_connect_home, "linux_x86", "bin", "customized.java.path")
    java_path_linux64 = os.path.join(db_connect_home, "linux_x86_64", "bin", "customized.java.path")
    java_path_win32 = os.path.join(db_connect_home, "windows_x86", "bin", "customized.java.path")
    java_path_win64 = os.path.join(db_connect_home, "windows_x86_64", "bin", "customized.java.path")

    java_home_files = [
        {"filename": java_path_darwin, "suffix": "/bin/java"},
        {"filename": java_path_linux32, "suffix": "/bin/java"},
        {"filename": java_path_linux64, "suffix": "/bin/java"},
        {"filename": java_path_win32, "suffix": "\\bin\\java.exe"},
        {"filename": java_path_win64, "suffix": "\\bin\\java.exe"}
    ]
    for java_home_file in java_home_files:
        _add_write_file_operation(java_home_file['filename'], java_home + java_home_file['suffix'])

    java_stanza = service.confs['dbx_settings']['java']
    to_update = {
        'javaHome': java_home
    }
    _add_update_operation("dbx_settings.conf", java_stanza, to_update)


def _update_java_command_filename(service):
    def update_commands_conf_action():
        java_commands = ["dbxquery", "dbxoutput", "dbxlookup"]
        commands_endpoint = "configs/conf-commands/%s"
        for java_command in java_commands:
            entity = client.Entity(service, commands_endpoint % java_command)
            entity.update(**{"filename": "customized.java.path"}).refresh()
    actions.append(Action("update customized.java.path in commands.conf", update_commands_conf_action))


def check_inputs_conf_rpcserver(service):
    configs = {
        "index": "_internal",
        "options": "-XX:+UseConcMarkSweepGC",
        "port": 9998,
        "bindIP": "127.0.0.1",
        "interval": 15,
        "useSSL": False,
        "disabled": False,
        "protocol": "TLS",
        "cipherSuite": "none",
        "cert_file": "default.jks",
        "cert_validity": 731,
        "keystore_password": "password",
    }

    section = "rpcstart://default"
    if section in service.confs["inputs"]:
        stanza = service.confs["inputs"][section]
        if _is_key_exist(stanza, "javahome"):
            configs['javahome'] = stanza['javahome']
        if _is_key_exist(stanza, "options"):
            configs['options'] = stanza['options']
        if _is_key_exist(stanza, "port"):
            configs['port'] = stanza['port']
        if _is_key_exist(stanza, "bindIP"):
            eprint("bindIP won't be migrated")
        if _is_key_exist(stanza, 'disabled') and _normalize_boolean(stanza['disabled']):
            eprint("Because the rpcserver is disabled, the DBX3 java server will also be disabled after migration completes.")
            configs['disabled'] = True
        if _is_key_exist(stanza, 'protocol') or _is_key_exist(stanza, 'cipherSuite') \
            or _is_key_exist(stanza, 'cert_file') or _is_key_exist(stanza, 'cert_validity') \
            or _is_key_exist(stanza, 'keystore_password'):
            eprint("customized SSL settings for rpcserver found, these will not be migrated")
        actions.append(Action("remove stanza {}".format(section), lambda: stanza.delete()))

    if 'javahome' in configs:
        java_home = configs['javahome']
    elif not running_on_deployer:
        if "JAVA_HOME" in os.environ:
            java_home = os.environ["JAVA_HOME"].replace('"', '')
        else:
            java_home = JavaHomeDetector.detect()
    else:  # we need give up detect java home on deployer
        java_home = ""

    if java_home != "":
        _update_java_home(service, java_home)
        _update_java_command_filename(service)
    else:
        eprint("java home cannot be found. Please setup from DBX UI after migration")

    jvm_options = configs['options']
    if configs['port'] != 9998:
        jvm_options += " -Ddw.server.applicationConnectors[0].port={}".format(configs['port'])

    jvm_option_conf_file = os.path.join(db_connect_home, "jars", "server.vmopts")
    if os.path.exists(jvm_option_conf_file):
        eprint("found existing file {}, already migrated?".format(jvm_option_conf_file))

    _add_write_file_operation(jvm_option_conf_file, jvm_options)

    server_stanza = service.confs["inputs"]["server://default"]  # use conf api in case jvm can not be started
    if configs['disabled']:
        _add_enable_disable_stanza_operation("inputs.conf", server_stanza, False)


def _filter_content(properties, white_list):
    return dict((k, v) for k, v in properties.iteritems() if k in white_list)


def _check_stanza_acl(stanza):
    return (stanza.access['app'] != DB_CONNECT_APP_NAME and stanza.access['sharing'] != "app") or stanza.access['app'] == DB_CONNECT_APP_NAME


def _get_stanza_namespace(stanza):
    return client.namespace(sharing=stanza.access['sharing'], owner=stanza.access['owner'], app=stanza.access['app'])


def check_inputs_conf_mi_input(service, service_with_dbx_ns):
    if "inputs" in service.confs:
        all_inputs = filter(lambda s: s.name.startswith("mi_input://"), service.confs["inputs"])
        all_inputs = filter(lambda s: s.access['app'] == service.namespace.app, all_inputs)
    else:
        all_inputs = []

    if len(all_inputs) > 0 and not _is_key_exist(service.confs, "db_inputs"):
        actions.append(Action("create db_inputs.conf for app {}".format(service.namespace.app),
                              lambda: service.confs.create("db_inputs")))

    for an_input in all_inputs:
        if not _check_stanza_acl(an_input):
            eprint("inputs.conf stanza {} in app {} cannot be migrated because of permission settings, "
                   "sharing:{}".format(an_input.name, an_input.access['app'], an_input.access['sharing']))
            continue

        properties = an_input.content
        name = an_input.name[len("mi_input://"):]

        mode = an_input['mode']
        if mode == "tail":
            query = an_input['query']
            rising_column_name = an_input['tail_rising_column_name']

            if _is_key_exist(an_input, 'enable_query_wrapping'):
                wrapped = _normalize_boolean(an_input['enable_query_wrapping'])
            else:
                if 'db_connections' in service.confs and an_input['connection'] in service.confs['db_connections']:
                    connection = service.confs['db_connections'][an_input['connection']]
                elif 'db_connections' in service_with_dbx_ns.confs and \
                        an_input['connection'] in service_with_dbx_ns.confs['db_connections']:
                    connection = service_with_dbx_ns.confs['db_connections'][an_input['connection']]
                else:
                    eprint("inputs.conf stanza {} in app {} cannot be migrated because its connection {} "
                           "can not be found".format(an_input.name, an_input.access['app'], an_input['connection']))
                    continue

                if _is_key_exist(connection, 'enable_query_wrapping'):
                    wrapped = _normalize_boolean(connection['enable_query_wrapping'])
                else:
                    wrapped = True  # default to True if not configured in db_connectons.conf
            if wrapped:
                query = "SELECT * FROM ({}) t WHERE {} > ?".format(query, rising_column_name)
            else:
                query = "{} WHERE {} > ?".format(query, rising_column_name)

            query = "{} ORDER BY {} ASC".format(query, rising_column_name)

            properties['mode'] = 'rising'
            properties['query'] = query

        if mode in ['tail', 'advanced', 'rising'] and not running_on_deployer:
            if _is_key_exist(an_input, "tail_rising_column_checkpoint_value"):
                value = an_input['tail_rising_column_checkpoint_value']
                filename = an_input.name[len("mi_input://"):]
                # we apply the same normalization as the backend: replace special characters and lower case the input name
                filename = re.sub(r'[^\w\-]', "_", filename).lower()
                full_path = os.path.join(check_point_dir, filename)

                content = collections.OrderedDict()
                content['value'] = value
                content['appVersion'] = "2.x"
                content['columnType'] = None
                content['timestamp'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                _add_write_file_operation(full_path, json.dumps(content) + "\n", mode="w+")
            else:
                eprint("checkpoint value is missing in {} mode input {}, "
                       "you need edit and save it in the UI after migration.".format(mode, name))

        properties['namespace'] = _get_stanza_namespace(an_input)
        _add_create_stanza_action(service, "db_inputs", name, _filter_content(properties, DB_INPUTS_WHITE_LIST_3_0), an_input.access)
        _add_remove_stanza_action("inputs.conf", an_input)


def check_inputs_conf_mi_output(service):
    if "inputs" in service.confs:
        all_outputs = filter(lambda s: s.name.startswith("mi_output://"), service.confs["inputs"])
        all_outputs = filter(lambda s: s.access['app'] == service.namespace.app, all_outputs)
    else:
        all_outputs = []

    if len(all_outputs) > 0 and not _is_key_exist(service.confs, "db_outputs"):
        actions.append(Action("create db_outputs.conf for app {}".format(service.namespace.app),
                              lambda: service.confs.create("db_outputs")))

    for an_output in all_outputs:
        if not _check_stanza_acl(an_output):
            eprint("inputs.conf stanza {} in app {} cannot be migrated because of permission settings, "
                   "sharing:{}".format(an_output.name, an_output.access['app'], an_output.access['sharing']))
            continue

        properties = an_output.content
        name = an_output.name[len("mi_output://"):]

        if 'query' in properties:
            if 'table_name' not in properties or not properties['table_name']:
                table_name_array = re.split(" +", properties['query'])
                if len(table_name_array) < 6:
                    eprint("Error occured for stanza {} in inputs.conf, query value is not recognised. You need to migrate the stanza manually.".format(an_output.name))
                    eprint("Delete the query property and add a new property table_name. The value should be the output table name.")
                    eprint("Then restart splunk and rerun the migration script.")
                    _quit_with_description("abort", -1)
                else:
                    properties['table_name'] = table_name_array[2]

        properties['namespace'] = _get_stanza_namespace(an_output)
        _add_create_stanza_action(service, "db_outputs", name, _filter_content(properties, DB_OUTPUTS_WHITE_LIST_3_0), an_output.access)
        _add_remove_stanza_action("inputs.conf", an_output)


def check_inputs_conf_mi_lookup(service):
    if "inputs" in service.confs:
        all_lookups = filter(lambda s: s.name.startswith("mi_lookup://"), service.confs["inputs"])
        all_lookups = filter(lambda s: s.access['app'] == service.namespace.app, all_lookups)
    else:
        all_lookups = []

    if len(all_lookups) > 0 and not _is_key_exist(service.confs, "db_lookups"):
        actions.append(Action("create db_lookups.conf for app {}".format(service.namespace.app),
                              lambda: service.confs.create("db_lookups")))

    for a_lookup in all_lookups:
        if not _check_stanza_acl(a_lookup):
            eprint("inputs.conf stanza {} in app {} cannot be migrated because of permission settings, "
                   "sharing:{}".format(a_lookup.name, a_lookup.access['app'], a_lookup.access['sharing']))
            continue
        properties = a_lookup.content
        name = a_lookup.name[len("mi_lookup://"):]
        properties['namespace'] = _get_stanza_namespace(a_lookup)
        _add_create_stanza_action(service, "db_lookups", name, _filter_content(properties, DB_LOOKUPS_WHITE_LIST_3_0), a_lookup.access)
        _add_remove_stanza_action("inputs.conf", a_lookup)


def check_inputs_conf_mi_session(service):
    all_sessions = filter(lambda s: s.name.startswith("mi_session://"), service.confs["inputs"])
    all_sessions = filter(lambda s: s.access['app'] == service.namespace.app, all_sessions)
    for s in all_sessions:
        actions.append(Action("remove mi_session stanza, name {}".format(s.name), lambda: s.delete()))


def _get_splunk_url(args):
    try:
        url = urlparse.urlparse("https://localhost:8089")
        if args.scheme is not None:
            url = url._replace(scheme=args.scheme)
        if args.port is not None:
            url = url._replace(netloc="localhost:{}".format(args.port))

        return url
    except Exception as ex:
        _quit_with_description("invalid command line arguments, cause: %s" % str(ex))


def _yes_or_no(prompt):
    while True:
        ans = raw_input(prompt)
        if ans == "Y":
            return True
        elif ans == "n":
            return False


def _create_service(username, password, url, app="-"):
    try:
        return client.connect(username=username, password=password, scheme=url.scheme, host=url.hostname, port=url.port, app=app)
    except Exception as ex:
        _quit_with_description("failed to login to splunkd, cause={}".format(ex))


def check_user_capability(service):
    required_capabilities = ['db_connect_read_identity', 'db_connect_read_dbinput', 'db_connect_create_dbinput',
                             'db_connect_update_dbinput', 'db_connect_delete_dbinput', 'db_connect_read_dboutput',
                             'db_connect_create_dboutput', 'db_connect_update_dboutput', 'db_connect_delete_dboutput',
                             'db_connect_read_dblookup', 'db_connect_create_dblookup', 'db_connect_update_dblookup',
                             'db_connect_delete_dblookup', 'db_connect_read_resource_pool', 'db_connect_create_identity',
                             'db_connect_update_identity', 'db_connect_delete_identity', 'db_connect_read_connection',
                             'db_connect_create_connection', 'db_connect_update_connection', 'db_connect_delete_connection',
                             'db_connect_request_status', 'db_connect_execute_query', 'db_connect_request_metadata',
                             'db_connect_use_custom_action', 'db_connect_read_app_conf', 'db_connect_write_app_conf',
                             'db_connect_read_settings', 'db_connect_update_settings', 'db_connect_read_loglevel',
                             'db_connect_update_loglevel', 'db_connect_migrate', 'db_connect_check_jre',
                             'db_connect_edit_connection_ssl']
    capabilities = service.capabilities

    if not all(cap in capabilities for cap in required_capabilities):
        _quit_with_description("lack of capability to run the script, please contact your system administrator", -1)


def _autodetect_java_home():
    if os.name == 'posix':
        cur_os = os.uname()[0]
        if cur_os == 'Darwin':
            return _autodetect_java_home_osx()
        else:
            return _autodetect_java_home_posix()
    elif os.name == 'nt':
        return _autodetect_java_home_win()
    else:
        return ""


def _autodetect_java_home_osx():
    path = "/System/Library/Frameworks/JavaVM.framework/Home"
    v = _get_java_version(path)
    if v:
        return path


def _get_java_executable(java_home):
    return os.path.join(java_home, 'bin', "java.exe" if os.name == 'nt' else 'java')


def _get_java_version(java_home):
    executable = _get_java_executable(java_home)
    if os.path.exists(executable):
        output, err = subprocess.Popen([executable] + ['-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        if output:
            m = re.search("(java|openjdk) version \"?([^\s\"]+)\"?", output, flags=re.MULTILINE)
            if m:
                return JavaVersion(m.group(2))
            raise JavaVersionException(
                "Unable to determine Java version: %s" % " ".join(output.strip().splitlines()))
    else:
        raise JavaVersionException("Java Home %s is not a Java installation directory!" % java_home)
    raise JavaVersionException("Unable to determine Java version!")


def _autodetect_java_home_posix():
    if "JAVA_HOME" in os.environ:
        path = os.environ['JAVA_HOME']
        v = _get_java_version(path)
        if v: return path
    return _test_java_in_path()


def _autodetect_java_home_win():
    try:
        import _winreg as reg

        root = r'SOFTWARE\JavaSoft\Java Runtime Environment'
        reg_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, root, 0, reg.KEY_ALL_ACCESS)
        versions = []
        for i in range(255):
            try:
                versions.append(reg.EnumKey(reg_key, i))
            except:
                break
        versions.sort(reverse=True)

        for version in versions:
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, "\\".join([root, version]), 0, reg.KEY_ALL_ACCESS)
            path = reg.QueryValueEx(key, "JavaHome")[0]
            if path and os.path.exists(path) and _get_java_version(path):
                return path
    except:
        pass


def _test_java_in_path():
    try:
        p = subprocess.Popen(['which', 'java'], stdout=subprocess.PIPE)
        out = p.communicate()[0]
        if out:
            path = os.path.normpath(os.path.join(os.path.realpath(out.strip()), '..', '..'))
            v = _get_java_version(path)
            if v: return path
    except:
        pass


class JavaVersionException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class JavaExecutionException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class JavaVersion:
    def __init__(self, str):
        self.str = str
        self.parts = str.split(".")

    def getMajor(self):
        return int(self.parts[0])

    def getMinor(self):
        return int(self.parts[1])

    def __str__(self):
        return self.str


class JavaHomeDetector(object):
    detected_java_home = None

    @classmethod
    def detect(cls):
        cls.detected_java_home = _autodetect_java_home()
        if cls.detected_java_home is None:
            cls.detected_java_home = ""  # platform specific detector may return None, normalize to empty str.
        return cls.detected_java_home


# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="migration tool argument parser")
    parser.add_argument("-scheme", help="the splunk server uri's scheme, either http or https", required=False)
    parser.add_argument("-port", help="the splunk server's management port, by default it is 8089", required=False)
    parser.add_argument("-verbose", help="whether enable verbose logging, default is False", required=False, action='store_true')
    args = parser.parse_args()

    verbose_logging = args.verbose
    url = _get_splunk_url(args)
    print(usage_message)

    username = raw_input("Username: ")
    password = getpass.getpass()

    service = _create_service(username, password, url, app=DB_CONNECT_APP_NAME)

    if "shc_deployer" in client.Entity(service, "server/roles").content.role_list:
        running_on_deployer = True
        print("Looks like you are running migrate on a deployer, extra steps need to be taken. Please note:")
        print("1. This script won't backup anything, please login to one of the SHC node and backup the whole /etc/apps folder")
        print("2. Scheduled inputs/outputs won't be supported on SHC any longer, please set up a heavy forwarder to run your scheduled inputs/outputs.")
        print("3. Make sure all JDBC drivers used on search heads are installed on this machine in the splunk_app_db_connect folder under bin/lib")
        print("4. Migration script requires the management API endpoint of one cluster node, in order to check the configuration")
        print("Please input the management API endpoint, For example: https://my-captain:8089")
        url = raw_input("API endpoint: ")
        url = urlparse.urlparse(url)
        username = raw_input("Username: ")
        password = getpass.getpass()
        service = _create_service(username, password, url, app=DB_CONNECT_APP_NAME)

    check_user_capability(service)

    installed_apps = map(lambda service: service.name, service.apps)

    if DB_CONNECT_APP_NAME not in installed_apps:
        _quit_with_description("%s not installed?" % DB_CONNECT_APP_NAME)

    if not running_on_deployer:
        check_file_to_be_backuped(installed_apps)

    check_drivers_to_be_migrated()

    for app in service.apps:
        if _normalize_boolean(app.disabled):
            continue
        service_with_ns = _create_service(username, password, url, app=app.name)
        print("checking db_connections.conf for app %s ..." % app.name)
        check_db_connections_conf(service_with_ns, service)

        print("checking db_connection_types.conf for app %s ..." % app.name)
        check_db_connection_types_conf(service_with_ns)

        print("checking inputs.conf for app %s ..." % app.name)
        if not running_on_deployer:
            check_point_dir = os.path.join(splunk_home, "var", "lib", "splunk", "modinputs", "server", DB_CONNECT_APP_NAME)
            if not os.path.exists(check_point_dir):
                actions.append(Action("create checkpoint dir at {}".format(check_point_dir), lambda: _mkdir_p(check_point_dir)))
        check_inputs_conf_mi_input(service_with_ns, service)
        check_inputs_conf_mi_output(service_with_ns)
        check_inputs_conf_mi_lookup(service_with_ns)
        check_inputs_conf_mi_session(service_with_ns)

    check_inputs_conf_rpcserver(service)  # only check for db_connect

    print("Migration actions preview:")
    total = 0
    for a in actions:
        total += 1
        print("[{}] ".format(total), a[0])

    if not _yes_or_no("app_migration.py is ready to apply the above actions, continue?[Y/n]"):
        _quit_with_description("aborted", 0)

    error_num = 0

    i = 0
    for a in actions:
        try:
            i += 1
            msg = "Performing action [{}/{}]:".format(i, total)
            print_progress(i, total, prefix=msg, suffix="Done!", bar_length=50)
            a[1]()
        except Exception as ex:
            eprint("\nfailed to execute action %s, cause:%s" % (i, str(ex)))
            error_num += 1
            if not _yes_or_no("Y to skip failed action and continue, n to abort the migration? [Y/n]"):
                _quit_with_description("aborted")

    print("Congratulations! Migration succeeded.")
    if error_num > 0:
        print("%s errors during migration. Please refer to the documentation to manually correct these, or "
              "contact the Splunk support team." % error_num)

    if running_on_deployer:
        print("Next step: run \'splunk apply shcluster-bundle\' to push the changes to cluster")
    else:
        print("Next step: Restart splunk and play around.")
