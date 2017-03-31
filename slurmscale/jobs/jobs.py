"""Get info about jobs running on this cluster."""
import pyslurm

from job import Job


class Jobs(object):
    """A service object to inspect jobs."""

    @property
    def _jobs(self):
        """Fetch fresh data."""
        return pyslurm.job().get()

    def list(self, states=None):
        """
        List the current jobs on the cluster.

        :type states: List of ``str``
        :param states: Filter jobs in the given states. Available states are
                      ``PENDING``, ``RUNNING``, ``CANCELLED``, ``CONFIGURING``,
                      ``COMPLETING``, ``COMPLETED``, ``FAILED``, ``TIMEOUT``,
                      ``PREEMPTED``, ``NODE_FAIL`` and ``SPECIAL_EXIT``.

        :rtype: List of ``Job``
        :return: A list of current cluster jobs, possibly filtered by supplied
                 states.
        """
        current_jobs = self._jobs
        jobs = []
        if states:
            for i in current_jobs:
                if current_jobs[i].get('job_state', '') in states:
                    jobs.append(Job(current_jobs[i]))
        else:
            jobs = [Job(current_jobs[j]) for j in current_jobs]
        return jobs
