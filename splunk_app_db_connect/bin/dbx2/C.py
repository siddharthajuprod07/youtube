
# connection parameter keywords
CONNECTION      = "connection"
JDBC_URL        = "jdbcUrlFormat"
JDBC_SSL_URL    = "jdbcUrlSSLFormat"
USERNAME        = "username"
PASSWORD        = "password"
READONLY        = "readonly"
QUERY           = "query"
UNIQUE_KEY      = "unique_key"
USING_UPSERT     = "using_upsert"
TEST_QUERY      = "testQuery"
CACHED          = "cached"
DRIVER_CLASS    = "jdbcDriverClass"
SERVICE_CLASS   = "serviceClass"
ISOLATION_LEVEL = "isolationLevel"
JDBC_USE_SSL    = "jdbcUseSSL"
USE_CONN_POOL   = "useConnectionPool"
RESOURCE_POOL   = "resource_pool"
CONNECTION_TYPE = "connection_type"
ENABLE_QUERY_WRAPPING   = "enable_query_wrapping"
DATABASE        = "database"
HOST            = "host"
PORT            = "port"


# lookup parameter keywords
KEY_PATTERN     = "key_pattern"
INPUT_FIELDS    = "input_fields"
OUTPUT_FIELDS   = "output_fields"
POLICY          = "policy"
POLICY_NONE     = "none"
POLICY_RELOAD   = "reload"
POLICY_UPDATE   = "update"
SQL_RELOAD      = "reloadSQL"
SQL_UPDATE      = "updateSQL"
SQL_LOOKUP      = "lookupSQL"
LAST_KEYS       = "lastkeys"

# health logger
LOGIN_USER        = "login_user"
HEALTH_LOGGERS    = "healthLoggers"
LOGGERS           = "loggers"
HIDDEN_PARAMETERS = "hiddens"

INIT_QUERY      = "query_init"
QUERY_TIMEOUT   = "query_timeout"
MAX_ROWS        = "max_rows"

QUERY_TABLE   = "ui_query_table"
QUERY_CATALOG = "ui_query_catalog"
QUERY_SCHEMA  = "ui_query_schema"

LOOKUP_OUT_MAP = "ui_column_output_map"
LOOKUP_IN_MAP = "ui_field_column_map"
LOOKUP_ALIAS_MAPPINGS = "lookup_alias"

_TIME = "##_time##"

NAME = "name"
IDENTITY = "identity"

NULL = "NULL"

TABLE_NAME = "table"
RELOAD = "reload"

MODE = "mode"

QUERY_MODE = "ui_query_mode"
SKIP_FIRST_RUN = "skipFirstRun"

INTERVAL = "interval"
DEFAULT_QUERY_TIMEOUT = 3600
URL_REQUEST_TIMEOUT = 600

_EVENT_TIME = "_$EVENT_TIME$_"

MAX_CONN_LIFETIME_MILLIS = "maxConnLifetimeMillis"
MAX_WAIT_MILLIS = "maxWaitMillis"
MAX_IDLE_CONN = "maxIdleConn"
MAX_TOTAL_CONN = "maxTotalConn"
CONNECTION_PROPERTIES = "connection_properties"
FETCH_SIZE = "fetch_size"
BATCH_UPLOAD_SIZE = "batch_upload_size"


DB_PARMS = [USE_CONN_POOL, JDBC_URL, JDBC_SSL_URL, JDBC_USE_SSL, DRIVER_CLASS, USERNAME, PASSWORD,
            SERVICE_CLASS, TEST_QUERY, READONLY, ISOLATION_LEVEL, QUERY_TIMEOUT,
            ENABLE_QUERY_WRAPPING, MAX_CONN_LIFETIME_MILLIS, MAX_WAIT_MILLIS, MAX_IDLE_CONN,
            MAX_TOTAL_CONN, CONNECTION_PROPERTIES, FETCH_SIZE, CONNECTION, BATCH_UPLOAD_SIZE]

# JRE parameters
JRE_INFO_OPTIONS='-XshowSettings:properties -version'
JRE_VERSION_KEY='java.vm.specification.version'
JRE_VENDOR_KEY='java.vendor'
JRE_VM_KEY='java.vm.name'
JRE_WANT_VERSION='1.8'
JRE_WANT_VENDOR='Oracle Corporation'
JRE_WANT_VM_ORACLEJDK = 'Java HotSpot(TM)'
JRE_WANT_VM_OPENJDK = 'OpenJDK'
JRE_WANTED_KEYS=[JRE_VERSION_KEY,JRE_VENDOR_KEY, JRE_VM_KEY]

RPC_PING = "RPC_PING"

INPUT = "input"
OUTPUT = "output"
LOOKUP = "lookup"



