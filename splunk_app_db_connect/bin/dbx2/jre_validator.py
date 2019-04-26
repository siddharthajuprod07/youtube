#! /usr/bin/env python
import os
from dbx_logger import logger
import threading
import subprocess
import traceback
import shlex
import C

class Command(object):
    """
    Enables to run subprocess commands in a different thread with TIMEOUT option.

    Based on jcollado's solution:
    http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933
    """
    command = None
    process = None
    status = None
    output, error = '', ''

    def __init__(self, command):
        if isinstance(command, basestring):
            command = shlex.split(command)
        self.command = command

    def run(self, timeout=None, **kwargs):
        """ Run a command then return: (status, output, error). """
        def target(**kwargs):
            try:
                self.process = subprocess.Popen(self.command, **kwargs)
                self.output, self.error = self.process.communicate()
                self.status = self.process.returncode
            except Exception as ex:
                self.error = traceback.format_exception_only(type(ex), ex)
                self.status = -1
        # default stdout and stderr
        if 'stdout' not in kwargs:
            kwargs['stdout'] = subprocess.PIPE
        if 'stderr' not in kwargs:
            kwargs['stderr'] = subprocess.PIPE
        # thread
        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
        return self.status, self.output, self.error


def matchesAny(line,values):
    return line.lstrip().startswith(tuple(values))

def validateJRE(javaCmd):
    attrs = {}
    reason = ""
    operation = "validate java command: {}.".format(javaCmd)

    if os.name == "nt":
        jreInfoCmd = '"%s" %s' % (javaCmd , C.JRE_INFO_OPTIONS)
    else:
        jreInfoCmd = '%s %s' % (javaCmd , C.JRE_INFO_OPTIONS)
    c = Command(jreInfoCmd)
    retval, output, error = c.run(10)

    if retval != 0:
        reason = error
        logger.debug(error)

        # smartly parse the error if we can.
        for line in error:
            if line.startswith("OSError:") or line.startswith("WindowsError"):
                reason = line

        isValid = False
        logger.critical(reason)
    else:
        pairs = [ line.lstrip().split(' = ', 2) for line in error.splitlines() if matchesAny(line, C.JRE_WANTED_KEYS)]

        for pair in pairs:
            k, v = pair
            attrs[k] = v

        version = attrs.get(C.JRE_VERSION_KEY,'')
        vendor = attrs.get(C.JRE_VENDOR_KEY,'')
        vm = attrs.get(C.JRE_VM_KEY,'')

        isValid = (version == C.JRE_WANT_VERSION and vendor == C.JRE_WANT_VENDOR and (vm.startswith(C.JRE_WANT_VM_ORACLEJDK) or vm.startswith(C.JRE_WANT_VM_OPENJDK)))
        if not isValid:
            reason = {"message": "Unsupported JRE detected",
                      "jre_using": "Using %s JRE version %s, %s" % (vendor, version, vm),
                      "jre_need": "Need Oracle Corporation JRE version 1.8 or OpenSDK 1.8"}
            logger.critical(reason)

    details = [str(reason), operation]

    return isValid, " ".join(details)

if os.name == 'nt':
    JAVA_DEPENDENCIES = [os.path.join("bin", "java.exe"),
                         os.path.join("bin", "keytool.exe")]

else:
    JAVA_DEPENDENCIES = [os.path.join("bin", "java"),
                         os.path.join("bin", "keytool")]

def checkDependencies(javaHome):
    reason = ""
    for dep in JAVA_DEPENDENCIES:
        fullPath = os.path.join(javaHome, dep)
        if not os.path.exists(fullPath):
            reason = "Missing JRE dependency: %s" % fullPath
            logger.critical(reason)
            return False, reason
    return True, reason
