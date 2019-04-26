#!/usr/bin/env sh

SCRIPT="$0"
cd `dirname "$SCRIPT"`

JAVA_PATH_FILE=`pwd -P`/customized.java.path
# goto darwin_x86_64 dir for jar file path defined in commands.conf
cd ..

if [ -f $JAVA_PATH_FILE ]; then
   JAVA_CMD=`cat $JAVA_PATH_FILE`
else
    JAVA_CMD="java"
fi

exec $JAVA_CMD $@
