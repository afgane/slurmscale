"""Monitor Slurm queue state and react by adding or removing nodes."""
import logging
import time

import slurmscale.jobs
import slurmscale.nodes

log = logging.getLogger(__name__)


def idle_nodes():
    """
    Check if there are idle nodes in the cluster.

    :rtype: ``bool``
    :return: True if the there are idle nodes in the cluster; False otherwise.
    """
    ns = slurmscale.nodes.Nodes()
    return True if len(ns.list(only_idle=True)) > 0 else False


def scale_down():
    """Remove idle nodes from the cluster."""
    ns = slurmscale.nodes.Nodes()
    log.debug("Scaling down (removing {0})".format(ns.list(only_idle=True)))
    ns.remove(ns.list(only_idle=True))


def waiting_jobs(grace=300):
    """
    Check if there are any jobs waiting in the queue that are ready to run.

    :type grace: ``int``
    :param grace: Number of seconds a job needs to be queued and ready to run
                  before it gets counted as waiting.

    :rtype: ``int``
    :return: Number of jobs that are ready to run
    """
    js = slurmscale.jobs.Jobs()
    jobs = js.list(states=['PENDING'])
    w_jobs = 0
    now = int(time.time())
    for job in jobs:
        if job.state_reason in ['Resources', 'Priority']:
            if now - grace > job.eligible_time:
                w_jobs += 1
    log.debug("We have {0} job(s) waiting to run".format(w_jobs))
    return w_jobs


def scale_up():
    """Add a worker node."""
    log.debug("Scaling up...")
    ns = slurmscale.nodes.Nodes()
    ns.add()


def setup_logging():
    """Setup logging."""
    formatter = logging.Formatter("%(asctime)s,%(msecs)d L#%(lineno)d "
                                  "[%(levelname)s] - %(message)s", "%H:%M:%S")
    console = logging.StreamHandler()  # log to console
    console.setFormatter(formatter)
    file = logging.FileHandler('/tmp/ac.log')
    file.setFormatter(formatter)

    log.addHandler(console)
    log.addHandler(file)
    log.setLevel(logging.DEBUG)
    # boto logger is chatty so slow it down a bit
    # logging.getLogger('boto').setLevel(logging.INFO)


def run_check():
    """Check if the cluster is busy or has idle nodes and initiate scaling."""
    if idle_nodes():
        scale_down()
    elif waiting_jobs():
        scale_up()

if __name__ == "__main__":
    setup_logging()
    while True:
        run_check()
        time.sleep(1800)  # Run every 30 minutes
