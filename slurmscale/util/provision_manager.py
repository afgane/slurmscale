"""A set of classes used to provision required resources."""
import paramiko
import socket
import subprocess
import time
from cloudbridge.cloud.factory import CloudProviderFactory
from cloudbridge.cloud.factory import ProviderList
from paramiko.ssh_exception import AuthenticationException
from paramiko.ssh_exception import BadHostKeyException
from paramiko.ssh_exception import SSHException

import slurmscale as ss

import logging
log = logging.getLogger(__name__)


class ProvisionManagerFactory(object):
    """A factory for provision managers."""

    @staticmethod
    def get_provision_manger(provision_manager_name):
        """
        Get a provision manager based on the supplied argument.

        :type provision_manager_name: ``str``
        :param provision_manager_name: Name of the provision manager class
                                       to instantiate. One of:
                                       ``JetstreamIUProvisionManager``

        :rtype: :class:`.provision_manager.ProvisionManager`
        :return: A provision manager object or ``None``.
        """
        if provision_manager_name == 'JetstreamIUProvisionManager':
            return JetstreamIUProvisionManager()
        assert 0, "Unrecognized provision manager: " + provision_manager_name


class ProvisionManager(object):
    """Instance provision manager interface."""

    def create(self, instance_name):
        """
        Provision a new instance/VM.

        :type instance_name: str
        :param instance_name: Name for the instance to be launched.

        :rtype: ``CloudBridge.Instance`` object
        :return: Launched instance object.
        """
        pass


class JetstreamIUProvisionManager(ProvisionManager):
    """A provisioner class for obtaining resources from Jetstream at IU."""

    def __init__(self):
        """Initialize target properties and credentials."""
        # ~/.cloudbridge file with access configs is required
        self.provider = CloudProviderFactory().create_provider(
            ProviderList.OPENSTACK, {})

        # Configs come from slurmscale.ini config file
        self.image_id = ss.config.get_config_value(
            'image_id', '1790e5c8-315a-4b9b-8b1f-46e47330d3cc')
        self.instance_type = ss.config.get_config_value(
            'instance_type', 'm1.large')
        self.network_id = ss.config.get_config_value(
            'network_id', '295cba46-10f0-4fd4-8494-c821c4c4098a')
        self.key_pair = ss.config.get_config_value(
            'key_pair', 'elasticity_kp')
        self.security_groups = ss.config.get_config_value(
            'security_groups', ['gxy-workers-sg', 'gxy-sg'])
        if not isinstance(self.security_groups, list):
            self.security_groups = self.security_groups.split(',')

    def _remove_known_host(self, host):
        """
        Remove a host from ~/.ssh/known_hosts.

        :type host: ``str``
        :param host: Hostname or IP address of the host to remove from the
                         known hosts file.

        :rtype: ``bool``
        :return: True if the host was successfully removed.
        """
        cmd = "ssh-keygen -R {0}".format(host)
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        if p.wait() == 0:
            return True
        return False

    def _check_ssh(self, ip, user='centos'):
        """
        Check for ssh availability on a host.

        This method assumes the default ssh key (~/.ssh/id_rsa) exists and will
        be used for authentication.

        :type ip: ``str``
        :param ip: IP address or hostname of the host to check.

        :type user: ``str``
        :param user: Username to use when trying to login.

        :rtype: ``bool``
        :return: True if ssh connection was successful.
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip, username=user)
            self._remove_known_host(ip)
            return True
        except (BadHostKeyException, AuthenticationException,
                SSHException, socket.error) as e:
            log.warn("ssh connection exception for {0}: {1}".format(ip, e))
        self._remove_known_host(ip)
        return False

    def create(self, instance_name):
        """
        Provision a new instance/VM.

        :type name: ``str``
        :param name: Name for the instance to be launched.

        :rtype: ``CloudBridge.Instance`` object
        :return: Launched instance object.
        """
        img = self.provider.compute.images.get(self.image_id)
        log.info("Starting a new instance named {0}".format(instance_name))
        inst = self.provider.compute.instances.create(
            name=instance_name, image=img, instance_type=self.instance_type,
            key_pair=self.key_pair, security_groups=self.security_groups,
            network=self.network_id)
        inst.wait_till_ready()
        while not self._check_ssh(inst.private_ips[0]):
            log.debug("Waiting for ssh on {0}...".format(inst.name))
            time.sleep(5)
        log.info("Instance {0} ({1}) started.".format(
                 inst.name, inst.private_ips[0]))
        return inst

    def delete(self, nodes):
        """
        Delete/terminate the supplied virtual machines.

        :type nodes: list of :class:`Node` objects
        :param nodes: List of nodes to terminate.
        """
        instances = self.provider.compute.instances.list()
        terminate = []
        for node in nodes:
            for instance in instances:
                if (node.ip in instance.private_ips and
                        node.name == instance.name):
                    terminate.append(instance)
        log.info("Deleting instances {0}".format(terminate))
        for instance in terminate:
            instance.terminate()
