# Copyright (C) 2005-2016 Splunk Inc. All Rights Reserved.
# The file contains the specification for database connections

[<name>]

serviceClass = <string>
# optional
# inherits from db_connection_types.conf if not configured
# java class that serves the jdbc service for this type.


customizedJdbcUrl = <string>
# optional
# the user customized jdbc url used to connect to the database.
# IF the value is empty a template will be used to generate the jdbc url.
# See jdbcUrlFormat and jdbcUrlSSLFormat defined in db_connection_types.conf.spec


jdbcUseSSL = [true | false]
# optional
# inherits from db_connection_types.conf if not configured
# default is false, whether this type of connection will support SSL connection.


jdbcDriverClass = <string>
# optional
# inherits from db_connection_types.conf if not configured
# java jdbc vendor driver class.


testQuery = <string>
# optional
# inherits from db_connection_types.conf if not configured
# If it is not configured here or in db_connection_types, then JdatabaseC isValid API
# will be used.
# SQL query to validate the connection to the database.


database = <string>
# required only when other parameters refer to.
# inherits from db_connection_types.conf if not configured
# The default database that the connection will use to connect to the database.


connection_type = <string>
# required
# The type of connection configured in db_connection_types.conf that the
# connection refers to


identity = <string>
# required
# The database identity that the connection will use when connecting to the
# database
# An identity provides username and password for database connection.
# See identities.conf.spec


isolation_level = <string>
# optional
# The transaction isolation level that the connection should use.
# Valid values are:
# - TRANSACTION_NONE,
# - TRANSACTION_READ_COMMITTED,
# - TRANSACTION_READ_UNCOMMITTED,
# - TRANSACTION_REPEATABLE_READ,
# - TRANSACTION_SERIALIZABLE,
# - DATABASE_DEFAULT_SETTING.
# default to DATABASE_DEFAULT_SETTING.


readonly = true|false
# optional
# default to false
# Whether the database connection is read-only.
# If it is readonly, any modifying SQL statement will be blocked.
# Note that property might not be supported by the JDBC driver, please consult
# your JDBX driver documentation for details.


host = <string>
# required only when other parameters refer to.
# The host name or IP of the database server for the connection
# Possible variable from jdbcUrlFormat.


port = <integer>
# required only when other parameters refer to.
# inherits from db_connection_types.conf if not configured
# The TCP port number that the host database server is listening to for
# connections.
# Possible variable from jdbcUrlFormat.


informixserver = <string>
# optional
# Required option for informix server to compose proper jdbc connection url.
# This attribute is used for informix server connection setup only.


useConnectionPool = true|false
# optional
# boolean to use a connection pool to the database
# defaults to true


connection_properties = <string>
# optional, differs for different databases.


fetch_size = <integer>
# optional, default is 100, the number of rows retrieved with each trip to the
# database.


maxConnLifetimeMillis = <value>
# optional, default is 120000 = 120 seconds
# valid when useConnectionPool = true
# The maximum lifetime in milliseconds of a connection. After this time is
# exceeded the connection will fail the next activation, passivation or
# validation test.
# A value of zero or less means the connection has an infinite lifetime.


maxWaitMillis = <value>
# optional, default is 30000 = 30 seconds
# valid when useConnectionPool = true
# The maximum number of milliseconds that the pool will wait (when there are no
# available connections) for a connection to be returned before throwing an
# exception.
# [250, 300000] milliseconds is a reasonable value to wait to establish a
# connection.  The max wait time is 300000 millisenconds (300 seconds).


minIdle = <integer>
# optional, default is 1 connection
# valid when useConnectionPool = true
# The minimum number of connections kept in this pool, this value must be less
# than maxTotalConn. The pool will dynamically grow up to maxTotalConn if
# required.

idleTimeout = <integer>
# optional, default is 600000 = 10 minutes
# The maximum amount of time that a connection is allowed to sit idle in the
# pool in milliseconds.
# valid when useConnectionPool = true and when minIdle is defined to be less
# than maxTotalConn.
# Whether a connection is retired as idle or not is subject to a maximum
# variation of +30 seconds, and average variation of +15 seconds.
# A connection will never be retired as idle before this timeout.
# Once the pool reaches minIdle connections, connections will no longer be
# retired, even if idle.
# A value of 0 means that idle connections are never removed from the pool.
# The minimum allowed value is 10000ms (10 seconds).


maxTotalConn = <integer>
# optional, default is 8 connections
# valid when useConnectionPool = true
# The maximum number of active connections that can be allocated from this pool
# at the same time. When the pool reaches this size, and no idle connections are
# available, getting a connection will block for up to maxWaitMillis
# milliseconds before timing out.


timezone = <time zone identifier>
# optional, default uses JVM time zone
# The identifier could be:
#  - an offset from UTC/Greenwich, that uses the same offset regardless given
# date-time e.g. +08:00
#  - an area where a specific set of rules for finding the offset from
# UTC/Greenwich apply e.g. Europe/Paris.


localTimezoneConversionEnabled = [true | false]
# optional, default is false
# valid when a time zone is set
# When turned on, time-related fields are read from the database using the
# configured time zone and then translated to the JVM time zone.
# For example, with a database using UTC and the JVM using GMT+8, the datetime
# field defined in the database 2017-07-21 08:00:00 will be displayed as
# 2017-07-21 16:00:00
