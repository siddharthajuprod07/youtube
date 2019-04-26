#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import datetime
import platform
import itertools
import logging

from logging.handlers import BaseRotatingHandler
from .cloghandler import ConcurrentRotatingFileHandler

__all__ = ('DBXRotatingFileHandler', )


class DBXRotatingFileHandler(ConcurrentRotatingFileHandler):

    """This class inherits from ConcurrentRotatingFileHandler which ensures
    data safety when logging with multiple processes. This handler works on
    Unix-like operating systems as well as Windows, although in some cases
    the rotating action under Windows may have a latency so that the size
    of log files may exceed the limit.

    This subclass enables the file handler to accept a parameter as the path
    to lock file instead of using current directory. Additionally due to some
    code changes this class no longer supports python version under 2.6 now.
    """
    DATE_FORMAT = ".%Y%m%d"

    def __init__(self, filename, lockfile='', mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=0, debug=True):
        filepath = os.path.abspath(filename)
        
        # Initially, if we are in degrade mode, process the filepath
        if self.isDegradeMode: filepath = self._getDegradeFilename(filepath)

        BaseRotatingHandler.__init__(self, filepath, mode, encoding, delay)

        self._rotateFailed = False
        self.maxBytes = maxBytes
        self.backupCount = backupCount

        self._open_lockfile(lockfile)

        if debug: self._degrade = self._degrade_debug

        if self.isDegradeMode:
            self._delete_logfiles() # Perform log cleaning action every time a new process is initialized

    @property
    def isDegradeMode(self):
        """Where the logger is working in degrade mode. Currently this method
        just return True under Windows and False under other platforms. In degrade mode,
        this handler will use date based rotating straitegy: logs are rotated day by day
        and only `backupCount` days of files will be keep. This degradeMode is added to resolve
        the log rotation problem under Windows

        :returns: bool
        """
        return platform.system() == "Windows"

    def shouldRollover(self, *args, **kwargs):
        if self.isDegradeMode:
            return self._degradeShouldRollover(*args, **kwargs)
        else:
            return ConcurrentRotatingFileHandler.shouldRollover(self, *args, **kwargs)

    def doRollover(self, *args, **kwargs):
        if self.isDegradeMode:
            self._degradeDoRollover(*args, **kwargs)
        else:
            ConcurrentRotatingFileHandler.doRollover(self, *args, **kwargs)

    def _get_lockfilename(self, lockfile):
        if lockfile.endswith('.log'): lockfile, _ = os.path.splitext(lockfile)
        if not lockfile.endswith('.lock'): lockfile += '.lock'
        return lockfile

    def _open_lockfile(self, lockfile=None):
        lockfile = lockfile or self.baseFilename

        lockfile = self._get_lockfilename(lockfile)

        dirname = os.path.dirname(lockfile)
        if not os.path.isdir(dirname): os.makedirs(dirname)
        self.stream_lock = open(lockfile, 'w')

    def _getDegradeFilename(self, filepath):
        """Append date string like '20160721' onto the filepath under degrade mode
        """
        date, path = self._parseDegradeFilename(filepath)
        # If we can not parse date from file path, directly append date suffix string
        if date is None: return filepath + self._dateSuffix()

        basename, datestr = os.path.splitext(filepath) # Drop old date string
        return basename + self._dateSuffix()

    def _dateSuffix(self, date=None):
        if date is None: date = datetime.date.today()
        return date.strftime(self.DATE_FORMAT)

    def _parseDegradeFilename(self, path):
        try:
            (base, ext) = os.path.splitext(path)
            date = datetime.datetime.strptime(ext, self.DATE_FORMAT).date()
            return date, path
        except ValueError as e:
            return None, path

    def _degradeShouldRollover(self, record):
        """Should rollover checking for degrade mode. The super handler rotate files
        based on filesize which means it may always returns True under degrade mode
        when current log file exceed the maxsize as we won't actually remove or move files
        in degrade mode.

        Instead, We check if current filename's date suffix should be changed when a new
        record comes and if True, we let the handler rotate.
        """
        old, path = self._parseDegradeFilename(self.baseFilename)
        # Return true if we can not parse date out of current log file's path
        if old is None: return True
        return self._dateSuffix(old) != self._dateSuffix()

    def _degradeDoRollover(self):
        """Perform degrade rollover on Windows. Degrade rollover is based on date related rotate strategy:
        logs are rotated day by day. This strategy only applys for Windows under which it is impossible
        to rotate log file while other processes are opening it. This method keeps only `backupCount` days
        of log files.
        """
        # As logs are automatically printing into files with date as suffix, there is no need
        # to move the file here. But we still need to rename the baseFilename and remove old log files.

        self.stream.close()
        self.stream_lock.close()

        self.release() # Close and release old log file
        # Rename current log file
        self.baseFilename = self._getDegradeFilename(self.baseFilename)

        self._open_lockfile()
        self.acquire() #  Acquire and open new log file

        self._delete_logfiles()

    def _delete_logfiles(self):
        # We should never delete the log file of today, neither that of yesterday
        # as we have to leave the log to exsits for a while for Splunk to have
        # enough time to index it.
        backupCount = max(self.backupCount, 2) 
        filelist = self._getLogFiles()
        to_delete = filelist[backupCount:]
        for path in to_delete:
            try:
                os.remove(path)
                lockfile = self._get_lockfilename(path)
                if os.path.exists(lockfile): os.remove(lockfile) 
            except:
                self._degrade(True, "Failed to delete log file: %s", path)

    def _getLogFiles(self):
        filepath = self.baseFilename
        (basename, ext) = os.path.splitext(filepath)
        files = glob.glob(basename + '.*')
        files.append(basename)
        parsed = [self._parseDegradeFilename(f) for f in files]
        withdate = reversed(sorted((d, p) for d, p in parsed if d is not None))
        nodate = sorted((d, p) for d, p in parsed if d is None if not p.endswith('.lock'))
        return [p for d, p in itertools.chain(withdate, nodate) if os.path.exists(p)]


logging.handlers.DBXRotatingFileHandler = DBXRotatingFileHandler
