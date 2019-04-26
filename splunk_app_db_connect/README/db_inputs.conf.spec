[<name>]
description = <string>
# optional
# Description for this input

interval = <integer|string>
# required
# interval to fetch data from DB and index them in Splunk
# It could be a number of seconds or a cron expression

index = <string>
# optional
# index to store events imported in Splunk
# If not specified default index is used
# default to 'default'

source = <string>
# optional
# source associated to events indexed
# By default, the stanza name will be used

sourcetype = <string>
# required
# source type associated to events indexed

host = <string>
# optional
# host associated to events indexed

mode = [batch|rising|advanced]
# required
# Operational mode.
# advanced is deprecated since DBX v3.1, use rising instead.

connection = <string>
# required
# Indicates the database connection to work on.

query = <string>
# required
# SQL statement to retrieve data from remote database connection.

query_timeout = <integer>
# optional
# the max execution time of a SQL, the default is 30 seconds.

max_rows = <integer>
# optional
# the max rows of data retrieval. the default is 0, which means unlimited.

fetch_size = <integer>
# optional
# The number of rows to return at a time from the database. The default is 300.

batch_upload_size = <integer>
# optional
# Number of rows to be uploaded to HEC in one batch.  Default is 1000.



tail_rising_column_name = <string>
# deprecated since DBX v3.1.0, using tail_rising_column_number instead.
# optional if batch mode
# at tail mode, the rising column is the column which is always rising as the checkpoint of the tail loading.

tail_rising_column_fullname = <string>
# deprecated since DBX v3.1.0, using tail_rising_column_number instead.
# optional if batch mode
# fullname of input tail rising column, currently this value is used by front end only.

tail_rising_column_number = <integer>
# required for advanced mode
# 1-based position of rising column in the data loading.


input_timestamp_column_name = <string>
# deprecated since DBX v3.1.0, using input_timestamp_column_number instead
# optional
# the input timestamp column name, the data of this column will be the event time. If not set, dbinput will use the current timestamp as the event time.

input_timestamp_column_fullname = <string>
# deprecated since DBX v3.1.0, using input_timestamp_column_number instead
# optional
# fullname of input timestamp column, currently this value is used by front end only.

input_timestamp_column_number = <integer>
# optional
# 1-based column number of input timestamp.


input_timestamp_format = <string>
# optional
# Specifies the format of input timestamp column, in JavaSimpleDateString format.
# with index_time_mode as dbColumn, if this property is provided then DBX will use ResultSet#getString to get the value
# and try to parse the timestamp with given format, else if this property is not persent DBX will try to use ResultSet#getTimestamp
# to get the timestamp.

index_time_mode = [current|dbColumn]
# required
# Specifies how to set the index time.
# current: use current time as index time
# dbColumn: use a DB column as index time.


max_single_checkpoint_file_size = <integer>
# optional
# Max checkpoint file size before archiving checkpoint file in bytes.  Default is 10MB, max is 100MB.


ui_query_mode = [simple|advanced]
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# Specifies whether the ui should use simple mode or adanced mode for SQL queries

ui_query_catalog = <string>
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# in simple mode, this value will be pre-populated into the catalog dropdown

ui_query_schema = <string>
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# in simple mode, this value will be pre-populated into the schema dropdown

ui_query_table = <string>
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# in simple mode, this value will be pre-populated into the query dropdown

template_name = <string>
# optional
# if provided and the value is not empty it means this input is created based on a template and the
# value is the name of the template.
