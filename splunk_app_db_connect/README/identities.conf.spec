# Copyright (C) 2005-2016 Splunk Inc. All Rights Reserved.
# The file contains the specification for database identities (username/password)

[<name>]

username = <string>
# required
# the username for this database connection identity

password = <string>
# required
# The encrypted value of the password for this database connection identity.

domain_name = <string>
# optional
# Specifies the windows domain name which the username belongs to

use_win_auth =  [true|false]
# optional
# Specifies wether the Windows Authentication Domain is used
