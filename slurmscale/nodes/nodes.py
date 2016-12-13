"""Represent and manage nodes of the target cluster."""
import pyslurm
import re

from .node import Node
from slurmscale.util.config_manager import ConfigManagerFactory
from slurmscale.util.provision_manager import ProvisionManagerFactory

import slurmscale as ss
ss.set_stream_logger(__name__)  # Uncomment to enable logging


class Nodes(object):
    """A service object to inspect and manage worker nodes."""

    def __init__(self, provision_manager_name='JetstreamIUProvisionManager',
                 config_manager_name='GalaxyJetstreamIUConfigManager'):
        """
        Initialize manager names.

        Nodes are managed by a provision manager and a config manager. Supply
        the class names for the respective managers.

        :type provision_manager_name: ``str``
        :param: provision_manager_name: Class name for the manager to be used
                                        when provisioning nodes. Only
                                        ``JetstreamIUProvisionManager`` is
                                        supported at the moment.

        :type config_manager_name: ``str``
        :param config_manager_name: Class name for the manager to be used
                                    when provisioning nodes. Only
                                    ``GalaxyJetstreamIUConfigManager`` is
                                    supported at the moment.
        """
        self.provision_manager_name = provision_manager_name
        self.config_manager_name = config_manager_name

    @property
    def _nodes(self):
        """Fetch fresh data."""
        return pyslurm.node().get()

    def list(self, only_idle=False):
        """
        List the nodes available on the cluster.

        :type only_idle: ``bool``
        :param only_idle: If set, return only IDLE nodes.

        :rtype: ``list`` of :class:`.Node`
        :return: A list of ``Node`` objects.
        """
        slurm_nodes = self._nodes
        current_nodes = []

        for n in slurm_nodes:
            if slurm_nodes.get(n).get('state') == 'IDLE':
                ss.log.trace("node {0} is IDLE".format(n))
                current_nodes.append(Node(slurm_nodes[n]))
            elif slurm_nodes.get(n).get('state') == 'IDLE' and not only_idle:
                ss.log.trace("node {0} is not IDLE".format(n))
                current_nodes.append(Node(slurm_nodes[n]))
        return current_nodes

    def _next_node_name(self, prefix):
        """
        Get the next logical node name.

        The returned name will be based on the supplied prefix with the
        number incremented from the largest available suffix. For example, if
        the following is a current list of nodes: ``jetstream-iu-large[0-5]``,
        the method will return ``jetstream-iu-large6``.

        :type prefix: ``str``
        :param prefix: Common prefix for the name across existing nodes.

        :rtype: ``str``
        :return: The next logical name with the supplied prefix.
        """
        largest_suffix = 0
        for node in self.list():
            if prefix in node.name:
                suffix = re.sub('^{0}'.format(prefix), '', node.name)
                try:
                    suffix = int(suffix)
                    if suffix > largest_suffix:
                        largest_suffix = suffix
                except ValueError as e:
                    ss.log.warn("Value error figuring out suffix {0} for node "
                                "{1}: {2}".format(suffix, node.name, e))
        name = "{0}{1}".format(prefix, largest_suffix + 1)
        ss.log.debug("Next node name: {0}".format(name))
        return name

    def add(self):
        """
        Add a new node into the cluster.

        This method will provision a new instance from a cloud provider and
        configure it for use with the cluster.

        TODO:
         - Allow a number of nodes to be added in one request
         - Allow type of instance to be specified, appropriately updating node
           name

        :rtype: ``bool``
        :return: ``True`` if adding a node was successful.
        """
        provision_manager = ProvisionManagerFactory.get_provision_manger(
            self.provision_manager_name)
        instance_name = self._next_node_name(
            prefix=ss.config.get_config_value('node_name_prefix',
                                              'jetstream-iu-large'))
        instance = provision_manager.create(instance_name=instance_name)
        self.configure([instance])

    def remove(self, node):
        """
        Remove a node from a cluster.

        This will disable the specified node and terminate the underlying
        machine.

        :type node: :class:`.Node`
        :param node: A node to remove from the cluster.

        :rtype: ``bool``
        :return: ``True`` if removal was successful.
        """
        raise NotImplementedError('Nodes.remove not implemented yet.')

    def configure(self, instances=None):
        """
        (Re)configure cluster nodes.

        This step will will run the configuration manager over any known
        nodes in the cluster plus any supplied instances.

        :type instances: list of ``cloudbridge.Instance`` objects
        :param instances: A list of instances/VMs to configure.
        """
        config_manager = ConfigManagerFactory.get_config_manager(
            self.config_manager_name)
        config_manager.configure(self.list(), instances)
