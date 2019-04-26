[<name>]
description = <value>
# optional
# Description for this output

interval = <string>
# required
# Specifies the interval to fetch data from Splunk and export to a database
# Valid only if scheduled is enabled
# It could be a number of seconds or cron expression

connection = <string>
# required
# Specifies the database connection to persist splunk data.

table_name = <string>
# required
# Specifies the table name used to export data.

using_upsert = [true|false]
# optional
# Specifies if upsert is used when exporting data to the table

unique_key = <string>
# required if upsert is enabled
# Specifies the column used as key to verify if the row needs to be inserted or updated.

query_timeout = <integer>
# optional
# Specifies the timeout (in seconds) for the SQL statement while exporting data.
# If the database supports batch operations, the timeout may apply to the whole
# batch or to each single statement. This behavior depends on the JDBC driver.
# For more information please consult the documentation of the driver about the
# following API Statement#setQueryTimeout.
# Default to 30 seconds.
# 0 means unlimited.

time_out = <integer>
# deprecated since DBX v3.1, use search_time_out and query_timeout instead.

search_timeout = <integer>
# optional
# Specifies the max time (in seconds) for a search job to run, if the search
# takes longer than this limit the job will be finalized then only part of the
# data will be exported.
# default is 0, which means unlimited.

search = <string>
# required
# Specifies the splunk search to pull data for output.
# If is_saved_search is enabled then this value specifies the saved search name.

query_earliest_time = <string>
# optional
# Specifies the earliest time applied to the search.
# The format is defined by Splunk time modifiers.
# default to null, which means no lower bound limit.

query_latest_time = <string>
# optional
# Specifies the latest time applied to the search.
# The format is defined by Splunk time modifiers.
# default to null, which means no upper bound limit.

is_saved_search = [true | false]
# optional
# specify the max time (in seconds) a search job can run, if time exceeded then search job will 
# be finalized then partial events will be outputted.
# default is 0, which means unlimited.

customized_mappings = <string>
# required
# Specifies the output data name (fieldx) and database column number (1...n) mappings.
# The expected format is:
#   field1:column1:type1,field2:column2:type2,…,fieldN:columnN:typeN
# For compatibility reason the following format is also supported but is deprecated:
#   field1:column1,field2:column2,…,fieldN:columnN

scheduled = [true|false]
# required
# Specifies wether the output is scheduled.
# An unscheduled output is typically used in dbxoutput command context.

ui_mappings = <string>
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# JSON mappings, purely for storage purposes

ui_selected_fields = <string>
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# JSON array of selected fields, purely for storage purposes

ui_saved_search_str = <string>
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# saved search string of the current saved search

ui_query_sql = <string>
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional

ui_query_mode = [simple|advanced]
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional

ui_query_catalog = <string>
# optional
# Specifies the table used to initialize the UI editor

ui_query_schema = <string>
# optional
# Specifies the schema used to initialize the UI editor

ui_query_table = <string>
# optional
# Specifies the table used to initialize the UI editor
