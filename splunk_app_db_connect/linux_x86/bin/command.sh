#!/usr/bin/env sh

SCRIPT=$(readlink -f "$0")
JAVA_PATH_FILE=$(dirname "$SCRIPT")/customized.java.path

if [ -f $JAVA_PATH_FILE ]; then
   JAVA_CMD=`cat $JAVA_PATH_FILE`
elif [ ! -z "$JAVA_HOME" ];then
    JAVA_CMD="$JAVA_HOME/bin/java"
else
    JAVA_CMD="java"
fi

exec $JAVA_CMD $@
