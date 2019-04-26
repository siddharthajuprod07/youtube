# Copyright (C) 2005-2016 Splunk Inc. All Rights Reserved.
# The file contains the specification for all db connect modular inputs
# # server - the modular input that runs java server

[server://<name>]
config_file = <string>
# required
# If the value is an absolute path, taskserver will treat it as the config_file path.
# If the value is a relative path, taskserver will prepend SPLUNK_HOME and generate the actual config_file path.
# On UNIX systems, a path is absolute if its prefix is "/".
# On Microsoft Windows systems, a path is absolute if its prefix is a drive specifier followed by "\\", or if its prefix is “\\\\”.

keystore_password = <string>
# required
# Specifies the java keystore password
# The keystore contains the certificate to set up the HTTPS connection to the
# task server.

interval = <integer>
# required
# Specifies the interval used by Splunkd to monitor Java server. If Java process
# is stopped, Splunkd will spawn a new Java process.
