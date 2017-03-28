SlurmScale is external library for delivering Slurm Elastic Computing.

## About

SlurmScale is a library written in Python that can be used to supply elastic
Slurm cluster scaling. Slurm comes with a [built-in support for elastic
computing](https://slurm.schedmd.com/elastic_computing.html) but it doesn't
appear to have seen any development or support for years so it's not really
functioning as expected. For example, if a `CLOUD` type Slurm node goes rogue,
[there is no way to remove the node from a
cluster](https://groups.google.com/forum/#!msg/slurm-
devel/QrVL4_Qc3uA/sDU6GeKrCwAJ;context-place=forum/slurm-devel). We also had an
issue with Ansible playbook threads not exiting when called by the provisioning
step. In response, here is a library that can be used to manage the dynamic
portion of a Slurm cluster.

The library can be used for basic Slurm cluster operations, such as listing
available cluster nodes, jobs and partitions, including the ability to disable
or enable them. Most notably, it can be used to add and remove nodes from a
cluster. The feature for adding a node consists or two steps: (1) provisioning
step, and (2) configuring step. The provisioning step creates a new instance on
a cloud provider while the configuration step integrates it into the cluster.
The implementation for these steps is pluggable accounting for flexibility.

## Setup

### Installing the library

The library is intended to be installed on a head node of a Slurm cluster. To
install, clone the repository and run the following commands. Note that, for
the time being, these instructions are tailored for use with Galaxy Project's
[infrastructure playbook](1). Take a look at the [README](https://github.com/
afgane/infrastructure-playbook/blob/custom_elastic/jetstreamiuenv/README.md)
in that playbook for instructions on how to modify the playbook configs so it
runs as expected. Also note that PySlurm must be installed on the system before
this library will install.

```
sudo -s
# If used w/o infra playbook: mkdir -p /opt/slurm_cloud_provision/
cd /opt/slurm_cloud_provision/
# If used w/o infra playbook: virtualenv .venv && source .venv/bin/activate
source bin/activate
# pip install -U virtualenv packaging appdirs setuptools
git clone https://github.com/afgane/slurmscale.git
cd slurmscale && python setup.py install
```

> ``pytz`` may fail to install as part of the overall setup step. Installing
it explicitly seems to work though: `pip install -U pytz`

Once installed, check the configuration settings in `slurmscale.ini`.
This configuration file can be placed in the root dir of the
library, in the user's home directory, or in `/etc/slurmscale.ini`.

```
cp slurmscale.ini.sample slurmscale.ini
vi slurmscale.ini
```

Internally, the library uses [CloudBridge
library](http://cloudbridge.readthedocs.io/) for cross-cloud compatibility so a
CloudBridge configuration file (`~/.cloudbridge`) is required in addition to
the SlurmScale config file. Galaxy infrastructure playbook will automatically
create this file. If you're not using that playbook, take a look at the
[CloudBridge documentation](2) for more details; here is an example of such
file for OpenStack:

```
[openstack]
os_username: username
os_password: password
os_auth_url: auth url
os_user_domain_name: user domain name
os_project_domain_name: project domain name
os_project_name: project name
```

### Installing the node configuration software

In order to configure a provisioned instance, you'll need to supply instance
configuration software. Again, if using the Galaxy infrastructure playbook, it
will place the necessary playbook. If the tool used for provisioning is not
already linked/configured within the library, you'll also need to make
appropriate changes so the library knows how to invoke the software; take a
look at `util/provision_manager.py` and `util/config_manager.py`.

## Use

Below is an example of usage. Each library method has a docstring with usage
details so refer to those for the details.

```
import slurmscale.jobs
import slurmscale.nodes
import slurmscale.partitions

jobs = slurmscale.jobs.Jobs()
jobs.list()

nodes = slurmscale.nodes.Nodes()
nodes.list()

partitions = slurmscale.partitions.Partitions()
partitions.list()

node = nodes.add()
node.state
node.enable()
node.state
nodes.remove(node)
```

## Logging

Library logging can be configured through `logging.yaml` file in the library's
root folder. By default (during the library's early days), the library will log
everything from the _DEBUG_ level messages to the console while the log file
will only capture _WARNING_ messages. The default log file location is the
library's root folder, called `slurmscale.log`. You can modify the the file
path and overall debug level in the appropriate handler, or add a logger for a
specific module if you'd like more logging granularity.


[1]: https://github.com/afgane/infrastructure-playbook/tree/custom_elastic
[2]: http://cloudbridge.readthedocs.io/en/latest/topics/setup.html#providing-access-credentials-in-a-file
