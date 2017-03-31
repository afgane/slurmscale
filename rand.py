"""Submit Slurm jobs at random intervals."""
import subprocess

from random import randint
from time import sleep

JOB_SCRIPT = "/home/centos/ts.sh"


def go():
    """Run forever, submitting a job at random intervals."""
    counter = 1
    while True:
        sleep_time = randint(60, 200)
        print("Sleeping %s seconds..." % sleep_time)
        sleep(sleep_time)
        print("Submitting job %s." % counter)
        subprocess.call(["sbatch", JOB_SCRIPT])
        counter += 1

if __name__ == "__main__":
    go()
