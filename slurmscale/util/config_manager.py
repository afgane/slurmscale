"""A set of classes used to configure resources into Slurm nodes."""

from .ansible import InventoryFile
# from .ansible.api import AnsibleRunner
from .ansible.cmd import AnsibleRunner

import slurmscale as ss


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

    def configure(self, nodes, instances=None):
        """
        Configure the supplied instances.

        TODO:
            - Make the paths configurable

        :type nodes: list of :class:``nodes.Node`` objects
        :param nodes: A list of worker nodes currently available in the system.

        :type instances: list of ``CloudBridge.Instance`` objects
        :param instances: A list of objects representing the target nodes.
        """
        cluster_nodes = []
        # Format info about any existing nodes into a dict
        for node in nodes:
            cluster_nodes.append({'name': node.name, 'ip': node.ip})
        # Format the new instance list
        if instances:
            for instance in instances:
                cluster_nodes.append({'name': instance.name,
                                      'ip': instance.private_ips[0]})
        ss.log.debug("Nodes to configure {0}".format(cluster_nodes))
        # Create the inventory file
        inventory_filename = ('/opt/slurm_cloud_provision/'
                              'infrastructure-playbook/jetstreamiuenv/inv')
        InventoryFile.create(inventory_filename, cluster_nodes)

        # Run ansible-playbook
        ss.log.info("Starting to configure nodes via ansible-playbook.")
        runner = AnsibleRunner(
            inventory_filename=inventory_filename,
            playbook_path=('/opt/slurm_cloud_provision/'
                           'infrastructure-playbook/jetstreamiuenv/'
                           'playbook.yml'),
            venv_path='/opt/slurm_cloud_provision')
        runner.run()
