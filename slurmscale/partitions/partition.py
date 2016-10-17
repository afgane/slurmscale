"""Represents and manage a cluster partition."""


class Partition(object):
    """Represent a cluster partition."""

    def __init__(self, partition):
        """Initialize the current object."""
        self._partition = partition

    @property
    def name(self):
        """Name of the partition, as reported by Slurm."""
        return self._partition.get('name')

    @property
    def state(self):
        """Partition state, as reported by Slurm."""
        return self._partition.get('state')

    def show(self):
        """
        Show complete details about this partition.

        *Note* that this method exists primarily for informational purposes.
        individual partition fields should be accessed through the object's
        properties.

        :rtype: ``dict``
        :return: A dictionary containing partition details.
        """
        return self._partition
