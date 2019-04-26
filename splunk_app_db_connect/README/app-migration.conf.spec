[<migrationId>]
# stanzas are identified by their migrationId
# a migrationId is used to decide which migration business logic to load and apply

STATE = <string>
# JSON encoded state store for all migrations of type <migrationId>

DEST_CONF = <string>
# by default the DEST_CONF will be <migrationId>. Use if we need to override,
# for example mi_input:// , mi_output://, and mi_lookup:// are all in inputs.conf but
# require different business logic for migration.