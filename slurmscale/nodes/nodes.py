"""Represent and manage nodes of the target cluster."""
import pyslurm

from node import Node

import slurmscale as ss
# ss.set_stream_logger(__name__)  # Uncomment to enable logging


class Nodes(object):
    """A service object to inspect and manage worker nodes."""

    @property
    def _nodes(self):
        """Fetch fresh data."""
        return pyslurm.node().get()

    def list(self, idle=False):
        """
        List the nodes available on the cluster.

        :type idle: ``bool``
        :param idle: If set, return only IDLE nodes.

        :rtype: ``list`` of :class:`.Node`
        :return: A list of ``Node`` objects.
        """
        slurm_nodes = self._nodes
        current_nodes = []

        for n in slurm_nodes:
            if idle and slurm_nodes.get(n).get('state') == 'IDLE':
                ss.log.trace("node {0} is IDLE".format(n))
                current_nodes.append(Node(slurm_nodes[n]))
            elif not idle:
                ss.log.trace("node {0} is not IDLE".format(n))
                current_nodes.append(Node(slurm_nodes[n]))
        return current_nodes
