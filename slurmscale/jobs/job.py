"""Represents a single job."""
import pyslurm


class Job(object):
    """An encapsulated Job object."""

    def __init__(self, job):
        """Initialize the Job object."""
        self._job = job

    def __repr__(self):
        """Return human-readable Job representation."""
        return "<SS-Job-{0} ({1})>".format(self.id, self.state)

    @property
    def id(self):
        """
        Get the ID of this job as reported by Slurm.

        :rtype: ``int``
        :return: Job ID number.
        """
        return self._job.get('job_id')

    @property
    def state(self):
        """
        Get the current state of this job as reported by Slurm.

        :rtype: ``str``
        :return: Job state; one of ``PENDING``, ``RUNNING``, ``CANCELLED``,
                 ``CONFIGURING``, ``COMPLETING``, ``COMPLETED``, ``FAILED``,
                 ``TIMEOUT``, ``PREEMPTED``, ``NODE_FAIL`` and ``SPECIAL_EXIT``
        """
        self.update()  # Always get fresh data
        return self._job.get('job_state')

    @property
    def eligible_time(self):
        """
        Time when the job became eligible to run. Applicable for PENDING jobs.

        :rtype: ``int``
        :return: Eligible time as a Unix timestamp. Return 0 if not available.
        """
        return self._job.get('eligible_time', 0)

    @property
    def run_time(self):
        """
        Time the job has taken to run. Valid jobs only.

        :rtype: ``int``
        :return: Runtime of the job.
        """
        self.update()  # Always get fresh data
        return self._job.get('run_time', 0)

    @property
    def state_reason(self):
        """
        The reason the job is in current state.

        :rtype: ``str``
        :return: One of the available Slurm reasons. See JOB REASON CODES on
                 https://slurm.schedmd.com/squeue.html
        """
        sr = self._job.get('state_reason')
        return None if sr == 'None' else sr  # Map string "None" to None

    def update(self):
        """Refresh info about the job by querying the scheduler."""
        self._job = pyslurm.job().find_id(str(self.id))[0]

    def show(self):
        """
        Show complete details about this job.

        *Note* that this method exists primarily for informational purposes;
        individual job fields should be accessed through the object's
        properties.

        :rtype: ``dict``
        :return: A dictionary containing job details, as provided by Slurm.
        """
        return self._job
