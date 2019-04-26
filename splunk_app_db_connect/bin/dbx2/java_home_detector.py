import os
import subprocess
import re
from dbx2.dbx_logger import logger

def _autodetect_java_home():
    if os.name == 'posix':
        cur_os = os.uname()[0]
        if cur_os == 'Darwin':
            return _autodetect_java_home_osx()
        else:
            return _autodetect_java_home_posix()
    elif os.name == 'nt':
        return _autodetect_java_home_win()
    else:
        logger.warn("Unable to autodetect JAVA_HOME on platform %s", os.name)
        return ""

def _autodetect_java_home_osx():
    path = "/System/Library/Frameworks/JavaVM.framework/Home"
    v = _get_java_version(path)
    if v: return path

def _get_java_executable(java_home):
    return os.path.join(java_home, 'bin', "java.exe" if os.name == 'nt' else 'java')

def _get_java_version(java_home):
    executable = _get_java_executable(java_home)
    if os.path.exists(executable):
        output, err = subprocess.Popen([executable] + ['-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        if output:
            m = re.search("(java|openjdk) version \"?([^\s\"]+)\"?", output, flags=re.MULTILINE)
            if m:
                return JavaVersion(m.group(2))
            raise JavaVersionException(
                "Unable to determine Java version: %s" % " ".join(output.strip().splitlines()))
    else:
        raise JavaVersionException("Java Home %s is not a Java installation directory!" % java_home)
    raise JavaVersionException("Unable to determine Java version!")

def _autodetect_java_home_posix():
    if "JAVA_HOME" in os.environ:
        path = os.environ['JAVA_HOME']
        v = _get_java_version(path)
        if v: return path
    return _test_java_in_path()


def _autodetect_java_home_win():
    try:
        import _winreg as reg

        root = r'SOFTWARE\JavaSoft\Java Runtime Environment'
        reg_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, root, 0, reg.KEY_ALL_ACCESS)
        versions = []
        for i in range(255):
            try:
                versions.append(reg.EnumKey(reg_key, i))
            except:
                break
        versions.sort(reverse=True)

        for version in versions:
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, "\\".join([root, version]), 0, reg.KEY_ALL_ACCESS)
            path = reg.QueryValueEx(key, "JavaHome")[0]
            if path and os.path.exists(path) and _get_java_version(path):
                return path
    except:
        pass

def _test_java_in_path():
    try:
        p = subprocess.Popen(['which', 'java'], stdout=subprocess.PIPE)
        out = p.communicate()[0]
        if out:
            path = os.path.normpath(os.path.join(os.path.realpath(out.strip()), '..', '..'))
            logger.debug("'which java' returned %s", path)
            v = _get_java_version(path)
            if v: return path
    except:
        pass


class JavaVersionException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class JavaExecutionException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class JavaVersion:
    def __init__(self, str):
        self.str = str
        self.parts = str.split(".")

    def getMajor(self):
        return int(self.parts[0])

    def getMinor(self):
        return int(self.parts[1])

    def __str__(self):
        return self.str

class JavaHomeDetector(object):
    detected_java_home = None

    @classmethod
    def detect(cls):
        cls.detected_java_home = _autodetect_java_home()
        if cls.detected_java_home is None:
            cls.detected_java_home = ""  # platform specific detector may return None, normalize to empty str.
        return cls.detected_java_home






