SlurmScale is external library for delivering Slurm Elastic Computing.

## About

SlurmScale is a library written in Python that can be used to supply elastic
cluster scaling. Slurm comes with a [built-in support for elastic
computing](https://slurm.schedmd.com/elastic_computing.html) but it doesn't
appear to have seen any development or support for years so it's not really
functioning as expected. For example, if a `CLOUD` type Slurm node goes rogue,
[there is no way to remove the node from a
cluster](https://groups.google.com/forum/#!msg/slurm-
devel/QrVL4_Qc3uA/sDU6GeKrCwAJ;context-place=forum/slurm-devel). We also had an
issue with  Ansible playbook threads not exiting when called by the provisioning
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
install, clone the repository and supply your configuration settings in
`slurmscale.ini`. This configuration file can be placed in the root dir of the
library, in the user's home directory or in `/etc/slurmscale.ini`.

```
mkdir -p /opt/slurm_cloud_provision/ && cd /opt/slurm_cloud_provision/
virtualenv .venv && source .venv/bin/activate
pip install -U setuptools
git clone https://github.com/afgane/slurmscale.git
cd slurmscale
python setup.py install
cp slurmscale.ini.sample slurmscale.ini
vi slurmscale.ini
```

> ``pytz`` may fail to install as part of the overall setup step. Installing it explicitly seems to work though: `pip install -U pytz`

Internally, the library uses [CloudBridge
library](http://cloudbridge.readthedocs.io/) for cross-cloud compatibility so a
CloudBridge configuration file (`~/.cloudbridge`) is required in addition to the
SlurmScale config file so create that file with your cloud access credentials.

### Installing the configuration software

In order to configure a provisioned instance, you'll need to suplly your
configuration software. If it's not already linked/configured within the
library, you'll also need to make appropriate changes so the library knows how
to invoke the software.

For Galaxy, the configuration software is [an Ansible
playbook](https://github.com/afgane/infrastructure-
playbook/tree/custom_elastic), so fetch a copy onto the master node:

```
cd /opt/slurm_cloud_provision
git clone https://github.com/afgane/infrastructure-playbook.git
```

As part of this step, take a look at the [README](https://github.com/afgane
/infrastructure-playbook/blob/custom_elastic/jetstreamiuenv/README.md) in that
playbook for instructions on how to modify the playbook configs so it runs as
expected.

## Use

For the time being, the library needs to be used from a Python prompt. Each
libary method has a doctring with usage details so refer to those for the
details. Here is an example of usage:

```
from slurmscale import jobs as ssjobs
from slurmscale import nodes as ssnodes
from slurmscale import partitions as sspartitions

jobs = ssjobs.Jobs()
jobs.list()

nodes = ssnodes.Nodes()
nodes.list()

partitions = sspartitions.Partitions()
partitions.list()

nodes.add()
node = nodes.list()[-1]
node.state
nodes.remove(node)
```

## Logging

Library logging can be configured through `logging.yaml` file in the library's
root folder. By default (during the library's early days), the library will log
everything from the _DEBUG_ level messages to the console while the log file
will only capture _WARNING_ messages. The default log file location is the
library's root folder. You can modify the the file path and overall debug level
in the appropriate handler, or add a logger for a specific module if you'd like
more logging granularity.
