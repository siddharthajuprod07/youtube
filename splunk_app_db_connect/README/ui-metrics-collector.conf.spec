# Copyright (C) 2005-2016 Splunk Inc. All Rights Reserved.
# This file contains possible attributes and values you can use to configure
# `ui-metrics-collector`.
#
# To set custom configurations, place a ui-metrics-collector.conf in
# $SPLUNK_HOME/etc/apps/<your_app>/local/. For examples, see ui-metrics-collector.conf.example.
# You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see
# the documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

[collector]
mode = [On | Off | None]
* The mode of analytics data collection with Party.js.
*   On       - users optted in, data will be collected.
*   Off      - users optted out, data will not be collected.
*   None     - awaiting users opt in or out, data will not be collected.
* Defaults to None.
* Values are case insensitive

app_id = <uuid_string>
* A UUID used to identify the Splunk App instance.
* This will be generated automatically when the Splunk user opts in the first time.
