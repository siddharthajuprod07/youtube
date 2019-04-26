import os
# this is optional but helps to make the logging format consistent
# when running custom splunk search command (dbxquery),
# Splunk will set TZ environment variable according to current user's account settings
# this will make timestamp in log formatted to user's local time zone (but still the same time)
# here we unset this environment variable to make time stamp always formatted to server's local time zone
if os.getenv('TZ'):
    os.unsetenv('TZ')

import datetime
import logging
import time
from datetime import timedelta, tzinfo


# defines canonical 0 time difference
ZEROTIME = timedelta(0)

# define local non-DST offset
STDOFFSET = timedelta(seconds = -time.timezone)

# defin local DST offset
if time.daylight:
    DSTOFFSET = timedelta(seconds = -time.altzone)
else:
    DSTOFFSET = STDOFFSET

# copied from ./lib/python2.7/site-packages/splunk/util.py
# TODO: simplify the implementation by introducing a third party lib?
class LocalTZInfo(tzinfo):
    '''
    Represents the local server's idea of its native timezone. Use when creating
    a timezone-aware datetime() object.

    Most invocations should use the singleton instance defined as splunk.util.localTZ
    '''

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTOFFSET - STDOFFSET
        else:
            return ZEROTIME

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        try:
            tt = (dt.year, dt.month, dt.day,
                  dt.hour, dt.minute, dt.second,
                  dt.weekday(), 0, -1)
            stamp = time.mktime(tt)
            tt = time.localtime(stamp)
            return tt.tm_isdst > 0
        except:
            return False
localTZ = LocalTZInfo()

ISO_8601_STRFTIME = '%Y-%m-%dT%H:%M:%S%z'

class DBXLoggingFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=ISO_8601_STRFTIME):
        date_time = datetime.datetime.fromtimestamp(record.created, localTZ)
        ts = date_time.strftime(datefmt)
        return ts