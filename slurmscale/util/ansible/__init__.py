"""A module for running Ansible-related steps."""
from string import Template

INVENTORY_TEMPLATE = Template("""
jetstream-iu0.galaxyproject.org ansible_connection=local

[baseenv]
jetstream-iu0.galaxyproject.org

[baseenv:children]
galaxynodes

# "contoller" node(s) for this cloud (not necessarily a slurm controller)
[controllers]
jetstream-iu0.galaxyproject.org

[slurmservers]
jetstream-iu0.galaxyproject.org

[slurmclients]
jetstream-iu0.galaxyproject.org

[slurmclients:children]
galaxynodes

[slurmelasticservers]
jetstream-iu0.galaxyproject.org

[cvmfsclients]
[cvmfsclients:children]
galaxynodes
controllers

[jetstreamnfsclients]
[jetstreamnfsclients:children]
galaxynodes

[slurmexechosts]
[slurmexechosts:children]
galaxynodes

[galaxynodes]
[galaxynodes:children]
jetstream-iu-large

[jetstream-iu-large]
#jetstream-iu-large0 ansible_host=10.0.0.72
${nodes}
""")


class InventoryFile(object):
    """Module for creating Ansible inventory file."""

    @staticmethod
    def create(file_path, nodes):
        """
        Create the inventory file.

        Currently, the inventory file is based on a pre-defined template
        where only the worker nodes are modified, according to the supplied
        argument.

        :type file_path: ``str``
        :param file_path: System path for the file where the inventory will be
                          stored. Note that an existing file will get
                          overwritten.

        :type nodes: ``list`` of ``dicts``
        :param nodes: A list of nodes to be added into the inventory file. Each
                      list item must be a dict with ``name`` and ``ip`` keys.
        """
        targets = []
        for node in nodes:
            targets.append("{0} ansible_host={1}".format(node.get('name'),
                                                         node.get('ip')))
        with open(file_path, 'w') as f:
            f.writelines(INVENTORY_TEMPLATE.substitute(
                         {'nodes': '\n'.join(targets)}))
