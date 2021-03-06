"""Represent and manage nodes of the target cluster."""
import re
from bunch import Bunch

import pyslurm

from .node import Node
from slurmscale.util.config_manager import ConfigManagerFactory
from slurmscale.util.provision_manager import ProvisionManagerFactory

import slurmscale as ss

import logging
log = logging.getLogger(__name__)


class Nodes(object):
    """A service object to inspect and manage worker nodes."""

    def __init__(self, provision_manager_name=None, config_manager_name=None):
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
        self._provision_manager_name = ss.config.get_config_value(
            'provision_manager_name', 'JetstreamIUProvisionManager')
        self._config_manager_name = ss.config.get_config_value(
            'config_manager_name', 'GalaxyJetstreamIUConfigManager')
        self._provision_manager = ProvisionManagerFactory.get_provision_manger(
            self._provision_manager_name)
        self._config_manager = ConfigManagerFactory.get_config_manager(
            self._config_manager_name)

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
            if only_idle:
                if slurm_nodes.get(n).get('state') == 'IDLE':
                    current_nodes.append(Node(slurm_nodes[n]))
            else:
                current_nodes.append(Node(slurm_nodes[n]))
        return current_nodes

    def get(self, name=None, ip=None):
        """
        Return a object representing the node identified by one of the args.

        It's necessary to supply only one argument. If both are supplied, the
        name takes precedence.

        :type name: ``str``
        :param name: Name of the node to try and get.

        :type ip: ``str``
        :param ip: IP address of the node to try and get.

        :rtype: object of :class:`.Node` or ``None``
        :return: An object representing the node, or None if a matching node
                 cannot be found.
        """
        for node in self.list():
            if name == node.name or ip == node.ip:
                return node
        return None

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
                    log.warn("Value error figuring out suffix {0} for node "
                             "{1}: {2}".format(suffix, node.name, e))
        # First node number starts at 0
        suffix = largest_suffix + 1 if largest_suffix or largest_suffix == 0 \
            else 0
        name = "{0}{1}".format(prefix, suffix)
        log.debug("Next node name: {0}".format(name))
        return name

    def add(self):
        """
        Add a new node into the cluster.

        This method will provision a new server from a cloud provider and
        configure it for use with the cluster.

        TODO:
         - Allow a number of nodes to be added in one request

        :rtype: object of :class:`.Node` or None
        :return: Return a handle to the new node that was added.
        """
        instance_name = self._next_node_name(
            prefix=ss.config.get_config_value('node_name_prefix',
                                              'jetstream-iu-large'))
        instance = self._provision_manager.create(instance_name=instance_name)
        inst = Bunch(name=instance.name, ip=instance.private_ips[0])
        ret_code, _ = self.configure(self.list() + [inst])
        if ret_code == 0:
            return self.get(name=instance_name)
        return None

    def remove(self, nodes, delete=True):
        """
        Remove nodes from the cluster.

        This will disable the specified nodes and terminate the underlying
        machine.

        :type nodes: list of :class:`.Node` or a single :class:`.Node` object
        :param nodes: Node(s) to remove from the cluster.

        :type delete: ``bool``
        :param delete: If ``True``, also delete VMs used by the removed nodes.

        :rtype: ``bool``
        :return: ``True`` if removal was successful.
        """
        log.debug("Removing nodes {0}".format(nodes))
        if not isinstance(nodes, list):
            nodes = [nodes]
        existing_nodes = set(self.list())
        keep_set = [node for node in existing_nodes if node not in nodes]
        delete_nodes = []  # Keep a copy (node info no longer available later)
        for node in nodes:
            delete_nodes.append(Bunch(name=node.name, ip=node.ip))
            node.disable(state=pyslurm.NODE_STATE_DOWN)
        ret_code, _ = self.configure(servers=keep_set)
        if ret_code == 0 and delete:
            log.debug("Reconfigured the cluster without node(s) {0}; deleting "
                      "the node(s) now.".format(nodes))
            self._provision_manager.delete(delete_nodes)
            return True
        return False

    def configure(self, servers):
        """
        (Re)configure the supplied servers as cluster nodes.

        This step will will run the configuration manager over the supplied
        servers and configure them into the current cluster.

        Note that the supplied list should contain any existing cluster nodes
        in addition to any new nodes. Only the supplied list of nodes will be
        configured as the cluster nodes.

        :type servers: list of objects with ``name`` and ``ip`` properties
        :param servers: A list of servers to configure. Each element of the
                        list must be an object (such as ``Node`` or ``Bunch``)
                        that has ``name`` and ``ip`` fields.

        :rtype: tuple of ``str``
        :return: A tuple with the process exit code and stdout.
        """
        return self._config_manager.configure(servers)
