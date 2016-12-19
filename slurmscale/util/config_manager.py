"""A set of classes used to configure resources into Slurm nodes."""

from .ansible import InventoryFile
# from .ansible.api import AnsibleRunner
from .ansible.cmd import AnsibleRunner

import logging
log = logging.getLogger(__name__)


class ConfigManagerFactory(object):
    """A factory for configuration managers."""

    @staticmethod
    def get_config_manager(config_manager_name):
        """
        Get a config manager based on the supplied argument.

        :type config_manager_name: ``str``
        :param config_manager_name: Name of the configuration manager class
                                    to instantiate. One of:
                                    ``GalaxyJetstreamIUConfigManager``

        :rtype: :class:`.config_manager.ConfigManager`
        :return: A configuration manager object or ``None``.
        """
        if config_manager_name == 'GalaxyJetstreamIUConfigManager':
            return GalaxyJetstreamIUConfigManager()
        assert 0, "Unrecognized config manager: " + config_manager_name


class ConfigManager(object):
    """Configuration manager interface."""

    def configure(self, instances):
        """
        Configure the supplied instances.

        :type instances: list of ``CloudBridge.Instance`` objects
        :param instances: A list of objects representing the target nodes.
        """
        pass


class GalaxyJetstreamIUConfigManager(ConfigManager):
    """Config manager for Galaxy node configuration on Jetstream at IU."""

    def configure(self, servers):
        """
        Configure the supplied servers.

        TODO:
            - Make the paths configurable

        :type servers: list of objects with ``name`` and ``ip`` properties
        :param servers: A list of servers to configure. Each element of the
                        list must be an object (such as ``Node`` or ``Bunch``)
                        that has ``name`` and ``ip`` fields.

        :type instances: list of ``CloudBridge.Instance`` objects
        :param instances: A list of objects representing the target nodes.

        :rtype: tuple of ``str``
        :return: A tuple with the process exit code and stdout.
        """
        nodes = []
        log.debug("Configuring servers {0}".format(servers))
        # Format server info into a dict
        for server in servers:
            nodes.append({'name': server.name, 'ip': server.ip})
        # Create the inventory file
        inventory_path = ('/opt/slurm_cloud_provision/'
                          'infrastructure-playbook/jetstreamiuenv/inv')
        InventoryFile.create(inventory_path, nodes)
        # Run ansible-playbook
        log.info("Starting to configure nodes via ansible-playbook.")
        runner = AnsibleRunner(
            inventory_filename=inventory_path,
            playbook_path=('/opt/slurm_cloud_provision/'
                           'infrastructure-playbook/jetstreamiuenv/'
                           'playbook.yml'),
            venv_path='/opt/slurm_cloud_provision')
        return runner.run()
