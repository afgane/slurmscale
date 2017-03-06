"""A module for running Ansible by wrapping command line."""
from os.path import join
import subprocess

import logging
log = logging.getLogger(__name__)


class AnsibleRunner(object):
    """Responsible for running Ansible playbook."""

    def __init__(self, playbook_root, inventory_filename, playbook_path,
                 venv_path, verbosity=0):
        """Initialized the runner."""
        self.inventory_filename = inventory_filename
        self.playbook_root = playbook_root
        self.playbook_path = playbook_path
        self.venv_path = venv_path
        self.verbosity = verbosity

    def run(self):
        """
        Run the initialized playbook.

        :rtype: tuple of ``str``
        :return: A tuple with the process exit code and stdout.
        """
        cmd = "cd {0} && ansible-playbook -i {1} {2}".format(
            self.playbook_root, self.inventory_filename, self.playbook_path)
        if self.venv_path:
            cmd = "source {0};{1}".format(join(self.venv_path, 'bin/activate'),
                                          cmd)
        log.debug("Running Ansible with command: {0}".format(cmd))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        p_status = p.wait()
        log.debug("Playbook stdout: %s\nstatus: %s" % (out, p_status))
        return (p_status, out)
