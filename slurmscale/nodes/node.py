"""Represents and manage a worker node."""


class Node(object):
    """Represent a worker node."""

    def __init__(self, node):
        """Initialize the current object."""
        self._node = node

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
