"""Represent and manage partitions of the target cluster."""
import pyslurm

from partition import Partition

import slurmscale as ss
# ss.set_stream_logger(__name__)  # Uncomment to enable logging


class Partitions(object):
    """A service object to inspect and manage cluster partitions."""

    @property
    def _partitions(self):
        """Fetch fresh data."""
        return pyslurm.partition().get()

    def list(self):
        """
        List the partitions available on the cluster.

        :rtype: ``list`` of :class:`.Partition`
        :return: A list of ``Partition`` objects.
        """
        current_partitions = self._partitions
        partitions = []
        for key in current_partitions.iterkeys():
            ss.log.trace("Adding partition {0} to .list".format(key))
            partitions.append(Partition(current_partitions[key]))
        return partitions
