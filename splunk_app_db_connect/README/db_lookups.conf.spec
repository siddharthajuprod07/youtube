[<name>]
description = <string>
# optional
# Description for this lookup

lookupSQL = <string>
# required
# Specifies the SQL query for lookups.

connection = <string>
# required
# Specifies the database connection to use.

output_column_map = <string>
# required
# Key/value pairs of database column to search result column in JSON format.

input_column_map = <string>
# required
# Key/value pairs of search result column to database column in JSON format.

ui_input_spl_search = <string>
# optional
# the splunk spl search which will be used for choosing lookup input_fields

ui_input_saved_search = <string>
# optional
# the splunk saved search which will be used for choosing lookup input_fields

ui_use_saved_search = [true|false]
# optional
# if true, then ui will use ui_input_saved_search
# if false, then ui will use ui_input_spl_search

input_fields = <string>
# deprecated since DBX v3.1.0, it is replaced by input_column_map
# Specifies the input fields for lookups.

output_fields = <string>
# deprecated since DBX v3.1.0, it is replaced by output_column_map
# Specifies the output fields after lookups.

ui_query_mode = [simple|advanced]
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# specify whether the ui should use simpple mode or adanced mode for SQL queries

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

ui_column_output_map = <string>
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# JSON mapping from db result column to field name

ui_field_column_map = <value>
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# JSON mapping from search result field to db column

ui_query_result_columns = <value>
# deprecated since DBX v3.1.0, it is ignored by the UI
# optional
# JSON encoded array of query result columns
# stores the columns from the associated lookupSQL
