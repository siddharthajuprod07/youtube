import os
import logging
import StringIO
import loghandlers

from logging.config import fileConfig


def _logging_conf_file(app_dir, default_or_local):
    return os.path.join(app_dir, default_or_local, 'dbx_logging.conf')


def _merge_local_if_exists(default_conf, local_conf):
    logging_conf_file = default_conf
    if os.path.exists(local_conf):
        with open(default_conf) as default, open(local_conf) as local:
            merged_conf = default.read() + local.read()
            logging_conf_file = StringIO.StringIO(merged_conf)
    return logging_conf_file


class DbxLoggerFactory(object):
    logging_conf_file = None
    app_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    default_conf = _logging_conf_file(app_dir, 'default')
    local_conf = _logging_conf_file(app_dir, 'local')

    @classmethod
    def create(cls, logger_name):
        error = None
        if not cls.logging_conf_file:
            try:
                logging_conf_file = _merge_local_if_exists(cls.default_conf, cls.local_conf)
                fileConfig(logging_conf_file, disable_existing_loggers=False)
            except Exception as e:
                logging_conf_file = cls.default_conf
                fileConfig(logging_conf_file, disable_existing_loggers=False)
                error = e
            finally:
                cls.logging_conf_file = logging_conf_file
                if cls.logging_conf_file and not isinstance(cls.logging_conf_file, str):
                    cls.logging_conf_file.close()

        logger = logging.getLogger(logger_name)
        if error:
            logger.error('action=failed_to_load_local_dbx_logging_conf loaded_logging_conf=default error=%s', error)
        return logger
