"""Represent and manage nodes of the target cluster."""
import pyslurm

from node import Node


class Nodes(object):
    """A service object to inspect and manage worker nodes."""

    def __init__(self):
        """Initialize the Nodes object."""
        self.nodes = pyslurm.node()

    def list(self):
        """List the nodes available on the cluster."""
        current_nodes = self.nodes.get()
        return [Node(current_nodes[n]) for n in current_nodes]
