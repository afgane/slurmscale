"""Represents and manage a worker node."""
import pyslurm


class Node(object):
    """Represent a worker node."""

    def __init__(self, node):
        """Initialize the current object."""
        self._node = node

    @property
    def name(self):
        """Name of the node, as reported by Slurm."""
        return self._node.get('name')

    @property
    def state(self):
        """Node state, as reported by Slurm."""
        return self._node.get('state')

    def _set_node_state(self, state, reason=None):
        """Set the node state to the provided argument."""
        node_dict = {
            'node_names': self.name,
            'node_state': state,
        }
        if reason:
            node_dict['reason'] = reason

        rc = pyslurm.node().update(node_dict)
        if rc == -1:
            return False
        return True

    def enable(self):
        """
        Enable this node to start processing jobs.

        :rtype: ``bool``
        :return: ``True`` if the node was successfully disabled.
        """
        return self._set_node_state(pyslurm.NODE_RESUME)

    def disable(self, state=pyslurm.NODE_STATE_DRAIN,
                reason="Disabled by SlurmScale"):
        """
        Disable this node from running jobs.

        :type state: ``int``
        :param state: Node state, one of ``pyslurm.NODE_STATE_DRAIN`` or
                      ``pyslurm.NODE_STATE_DOWN``.

        :type state: ``str``
        :param state: Reason for disabling the node.

        :rtype: ``bool``
        :return: ``True`` if the node was successfully disabled.
        """
        return self._set_node_state(state, reason)

    def show(self):
        """
        Show complete details about this node.

        *Note* that this method exists primarily for informational purposes.
        individual job fields should be accessed through the object's
        properties.

        :rtype: ``dict``
        :return: A dictionary containing node details.
        """
        return self._node
