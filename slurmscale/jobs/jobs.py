"""Get info about jobs running on this cluster."""
import pyslurm

from job import Job


class Jobs(object):
    """A service object to inspect jobs."""

    def __init__(self):
        """Initialize the jobs object."""
        self.jobs = pyslurm.job()

    def list(self):
        """List the current jobs on the cluster."""
        current_jobs = self.jobs.get()
        return [Job(current_jobs[j]) for j in current_jobs]
