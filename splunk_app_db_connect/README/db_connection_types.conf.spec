# Copyright (C) 2005-2016 Splunk Inc. All Rights Reserved.
# The file contains the specification for database connection types

[<name>]

serviceClass = <string>
# required
# Splunk Java class that provides JDBC support for this database connection type.


supportedVersions = <string>
# optional
# list (comma separated) supported verions(majorVersion.minorVersion) of JDBC driver implemented by serviceClass
# installed driver major version must == MajorVersion and minor version >= MinorVersion for a driver to be considered supported


jdbcUrlFormat = <string>
# required
# JDBC Connection URL used for this database connection type. Supported variables: host, port, database, informixserver.


jdbcUrlSSLFormat = <string>
# optional
# JDBC Connection URL used for this database connection type if jdbcUseSSL is enabled. Supported variables: host, port, database, informixserver.


jdbcUseSSL = [true | false]
# optional
# default is false, whether this type of connection will use SSL connection.


jdbcDriverClass = <string>
# optional
# Driver vendor Java class that provides JDBC support for this database connection type.


testQuery = <string>
# optional
# simple SQL to test validation for this database type.
# JDBC 4 compliant drivers do not need this parameter.


displayName = <string>
# optional
# Describe the database connection type for end users.


database = <string>
# required if used in jdbcUrlFormat or jdbcUrlSSLFormat.
# JDBC URL variable for the default database or schema used for this database connection type.


port = <integer>
# required if used in jdbcUrlFormat or jdbcUrlSSLFormat.
# JDBC URL variable for the network port used for this database connection type.


useConnectionPool = [true | false]
# optional, default is true.
# The connection pooling is based on Hikari, refer to https://github.com/brettwooldridge/HikariCP


ui_default_catalog = <string>
# optional
# ignored since 3.0


ui_default_schema = <string>
# optional
# ignored since 3.0


maxConnLifetimeMillis = <integer>
# optional, default is 120000 = 120 seconds
# valid when useConnectionPool = true
# The maximum lifetime in milliseconds of a connection in the connection pool.
# An in-use connection will never be retired, only when it is closed will it then be removed.
# A value of zero means the connection has an infinite lifetime.


maxWaitMillis = <integer>
# optional, default is 30000 = 30 seconds
# valid when useConnectionPool = true
# The maximum number of milliseconds that the pool will wait (when there are no
# available connections) for a connection to be returned before throwing an exception.
# [250, 300000] milliseconds is a reasonable value to wait to establish a connection.
# The max wait time is 300000 millisenconds (300 seconds).


maxTotalConn = <integer>
# optional, default is 8 connections
# valid when useConnectionPool = true
# The maximum number of active connections that can be allocated from this pool at the same time, or negative for no limit.


connection_properties = <string>
# optional
# Set JDBC variables for this database connection type.
# For example: {"useLegacyDatetimeCode": false}
