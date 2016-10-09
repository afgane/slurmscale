"""Represents a single job."""
import pyslurm


class Job(object):
    """An encapsulated Job object."""

    def __init__(self, job):
        """Initialize the Job object."""
        self.job = job

    @property
    def id(self):
        """
        Get the ID of this job as reported by Slurm.

        :rtype: ``int``
        :return: Job ID number.
        """
        return self.job.get('job_id')

    @property
    def job_state(self):
        """
        Get the current state of this job as reported by Slurm.

        :rtype: ``str``
        :return: Job state; one of ``PENDING``, ``RUNNING``, ``CANCELLED``,
                 ``CONFIGURING``, ``COMPLETING``, ``COMPLETED``, ``FAILED``,
                 ``TIMEOUT``, ``PREEMPTED``, ``NODE_FAIL`` and ``SPECIAL_EXIT``
        """
        return pyslurm.job().find_id(str(self.id))[0].get('job_state')

    def show(self):
        """
        Show complete details about this job.

        *Note* that this method exists primarily for informational purposes.
        individual job fields should be accessed through the object's
        properties.

        :rtype: ``dict``
        :return: A dictionary containing job details.
        """
        return self.job
