import re
import os
import os.path
from dbx2 import get_app_path
from dbx2.dbx_logger import logger

def _get_jvm_options_filepath():
    path = get_app_path()
    return os.path.join(path, "jars", "server.vmopts")

def write(jvm_options):
    jvm_options_file_path = _get_jvm_options_filepath()
    with open(jvm_options_file_path, "w") as vmopts_file:
        logger.debug("action=write_jvm_options_to_file, filepath=%sjvmopts=%s" % (jvm_options_file_path, jvm_options))
        vmopts_file.write(jvm_options)

def read():
    try:
        jvm_options_file_path = _get_jvm_options_filepath()
        if not os.path.isfile(jvm_options_file_path):
            logger.debug("action=jvm_options_file_not_exist, file_path=%s" % jvm_options_file_path)
            return ""
        with open(jvm_options_file_path, 'r') as vmopts_file:
            vmopts = vmopts_file.readline().strip()
            if not vmopts:
                return ""
            else:
                return vmopts
    except Exception as ex:
        logger.warn("action=fail_to_read_jvm_options_from_file", ex)
        return ""

def set_property(jvmopts, property, property_regex, value):
    prefix = " -D"
    if property in jvmopts:
        logger.debug("action=replace_property_value_in_jvm_options, property=%s value=%s property_regex=%s" %(property, value, property_regex))
        jvmopts= re.sub(property_regex, property + "=" + value, jvmopts)
    else:
        logger.debug("action=append_property_value_in_jvm_options, property=%s value=%s" %(property, value))
        jvmopts += (prefix + property + "=" + value)
    return jvmopts

def get_property(jvmopts, property, property_regex):
    vmopts = jvmopts.split(property)
    if len(vmopts) > 2:
        raise Exception(
            'failed to parse vmopts: too many property [%s] have been set' %property)
    matched = re.match(r'.*' + property_regex + r'.*', jvmopts)
    if matched:
        logger.debug("action=read_property_from_jvmoptions, jvmoptions=%s property=%s property_regex=%s" % (jvmopts, property, property_regex))
        return matched.group(1)
    else:
        logger.debug("action=fail_to_read_property_from_jvmoptions, jvmoptions=%s property=%s property_regex=%s" % (jvmopts, property, property_regex))
        return None
