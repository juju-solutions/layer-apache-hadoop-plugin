## Overview

This charm is intended to serve as a platform for Hadoop client software.
That is, software such as Apache Hive, or Apache Pig, which need to interact
with Hadoop as a client, but are not otherwise concerned with the details of
the particular distribution or deployment.  This charm is intended to make it
easy to create charms for that client software, by managing the Hadoop
libraries and connections.


## Usage: Creating Workload Charms

To create a charm which communicates with Hadoop, you only need to implement
a single relation interface: `hadoop-plugin`.  Your `metadata.yaml` should
contain:

    provides:
      hadoop-plugin:
        interface: hadoop-plugin

This is a subordinate relation which deploys this charm alongside the
workload charm.  The benefit of using this subordinate interface is that your
charm only needs to handle the single relation, it does not need to install or
manage the Apache Hadoop libraries, and it is decoupled from the distribution,
enabling easy swapping of the plugin from one distribution (in this case,
vanilla Apache Hadoop) with another.

Additionally, the `JAVA_HOME`, `HADOOP_HOME`, `HADOOP_CONF_DIR`, and other
environment variables will be set via `/etc/environment`.  This includes putting
the Hadoop bin and sbin directories on the `PATH`.  There are
[helpers](https://git.launchpad.net/bigdata-data/tree/common/noarch)
in `charmhelpers.contrib.bigdata.utils` to assist with using the environment
file. For example, to run the `hdfs` command to create a directory as the
`ubuntu` user:

    from charmhelpers.contrib.bigdata.utils import run_as
    run_as('ubuntu', 'hdfs', 'dfs', '-mkdir', '-p', '/home/ubuntu/foo')


## Provided Relations

  *There are no relations provided*

## Required Relations

### hadoop-plugin (interface: hadoop-plugin)

This relation connects this charm as a subordinate to the workload charm, as
described above.  The relation exchanges the following keys:

* Sent to the workload charm:

  * `hdfs-ready`: Flag indicating that HDFS is ready to store data

* Received from the workload charm:

  *There are no keys received from the workload charm*

To use this interface, it is recommended that you use the relation class
provided in the
[Juju Big Data library](https://pypi.python.org/pypi/jujubigdata). For example:

    from jujubigdata.relations import HadoopPlugin

    if HadoopPlugin().is_ready():  # wait for HDFS to be ready
        install_and_configure()


### namenode (interface: dfs)

This relation connects this charm to the apache-hadoop-hdfs-master charm.
The relation exchanges the following keys:

* Sent to hdfs-master:

  *There are no keys sent to the hdfs-master*

* Received from hdfs-master:

  * `private-address`: Address of the HDFS master unit, to be used as the NameNode
  * `has_slave`: Flag indicating if HDFS has at least one DataNode
  * `port`: Port where the NameNode is listening for HDFS operations (IPC)
  * `webhdfs-port`: Port for the NameNode web interface


### resourcemanager (interface: mapred)

This relation connects this charm to the apache-hadoop-yarn-master charm.
The relation exchanges the following keys:

* Sent to yarn-master:

  *There are no keys sent to the hdfs-master*

* Received from yarn-master:

  * `private-address`: Address of the YARN master unit, to be used as the ResourceManager
  * `has_slave`: Flag indicating if YARN has at least one NodeManager
  * `port`: Port where the ResourceManager is listening for YARN operations (IPC)
  * `historyserver-port`: JobHistory port (IPC)


## Manual Deployment

The easiest way to deploy an Apache Hadoop platform is to use one of
the [apache bundles](https://jujucharms.com/u/bigdata-charmers/#bundles).
However, to manually deploy the base Apache Hadoop platform without using one
of the bundles, you can use the following:

    juju deploy apache-hadoop-hdfs-master hdfs-master
    juju deploy apache-hadoop-hdfs-secondary secondary-namenode
    juju deploy apache-hadoop-yarn-master yarn-master
    juju deploy apache-hadoop-compute-slave compute-slave -n3
    juju deploy apache-hadoop-plugin plugin

    juju add-relation yarn-master hdfs-master
    juju add-relation secondary-namenode hdfs-master
    juju add-relation compute-slave yarn-master
    juju add-relation compute-slave hdfs-master
    juju add-relation plugin yarn-master
    juju add-relation plugin hdfs-master

This will create a scalable deployment with separate nodes for each master,
and a three unit compute slave (NodeManager and DataNode) cluster.  The master
charms also support co-locating using the `--to` option to `juju deploy` for
more dense deployments.
