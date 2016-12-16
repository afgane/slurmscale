"""Library setup."""
import logging
import logging.config
import os
import yaml

from util import Config

# Current version of the library
__version__ = '0.1.0'

lib_root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
config = Config()


def get_version():
    """
    Return a string with the current version of the library.

    :rtype: ``string``
    :return:  Library version (e.g., "0.1.0").
    """
    return __version__


def logpath(filename, max_bytes=0, backup_count=0):
    """
    Configure file log handler.

    Check the official docs for explanation of the fields:
    https://docs.python.org/2/library/logging.config.html#user-defined-objects
    """
    if not os.path.isabs(filename):
        filename = os.path.join(lib_root_path, filename)
    return logging.handlers.RotatingFileHandler(
        filename, maxBytes=max_bytes, backupCount=backup_count)

# Read log config from a YAML file
log_conf = os.path.join(lib_root_path, 'logging.yaml')
with open(log_conf, 'r') as f:
    logging.config.dictConfig(yaml.load(f))
log = logging.getLogger()
