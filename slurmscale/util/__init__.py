"""Utility module for factory classes."""
import os
from os.path import expanduser

try:
    from config_config_parser import SafeConfigParser
except ImportError:  # Python 2
    from ConfigParser import SafeConfigParser
# By default, use two locations for CloudBridge configuration
SlurmScaleConfigPath = '/etc/slurmscale.ini'
SlurmScaleConfigLocations = [SlurmScaleConfigPath]
UserConfigPath = os.path.join(expanduser('~'), '.slurmscale')
SlurmScaleConfigLocations.append(UserConfigPath)


class Config(object):
    """Library config class."""

    def __init__(self):
        """Initialize the config parser."""
        self._config_parser = SafeConfigParser()
        self._config_parser.read(SlurmScaleConfigLocations)

    def get_config_value(self, key, default_value):
        """
        Inspect the available configurations for the supplied key.

        :type key: ``str``
        :param key: Configuration value to retrieve.

        :type default_value: anything
        :param default_value: the default value to return if a value for the
                              ``key`` is not available

        :rtype: ``str``
        :return: a configuration value for the supplied ``key``
        """
        section_name = 'slurmscale'
        if (self._config_parser.has_option(section_name, key) and
                self._config_parser.get(section_name, key)):
            return self._config_parser.get(section_name, key)
        return default_value
