"""Represent and manage partitions of the target cluster."""
import pyslurm

from partition import Partition

import logging
log = logging.getLogger(__name__)


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
            log.debug("Adding partition {0} to .list".format(key))
            partitions.append(Partition(current_partitions[key]))
        return partitions
