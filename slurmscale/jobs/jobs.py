"""Get info about jobs running on this cluster."""
import pyslurm

from job import Job


class Jobs(object):
    """A service object to inspect jobs."""

    @property
    def _jobs(self):
        """Fetch fresh data."""
        return pyslurm.job().get()

    def list(self):
        """List the current jobs on the cluster."""
        current_jobs = self._jobs
        return [Job(current_jobs[j]) for j in current_jobs]
