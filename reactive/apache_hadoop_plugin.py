# pylint: disable=unused-argument
from charms.reactive import when, when_not, when_none, is_state
from charmhelpers.core.hookenv import status_set
from charms.hadoop import get_dist_config


@when('hadoop.installed', 'hadoop-plugin.joined')
def set_installed(client):
    dist = get_dist_config()
    client.set_installed(dist.hadoop_version)


@when('hadoop.installed', 'hadoop-plugin.joined')
@when('hadoop.hdfs.configured', 'namenode.ready')
def set_hdfs_ready(hdfs, client):
    client.set_hdfs_ready(hdfs.namenodes(), hdfs.port())


@when('hadoop.installed', 'hadoop-plugin.joined')
@when_not('namenode.ready')
def clear_hdfs_ready(client):
    client.clear_hdfs_ready()


@when('hadoop.installed', 'hadoop-plugin.joined')
@when('hadoop.yarn.configured', 'resourcemanager.ready')
def set_yarn_ready(yarn, client):
    client.set_yarn_ready(
        yarn.resourcemanagers(), yarn.port(),
        yarn.hs_http(), yarn.hs_ipc())


@when('hadoop.installed', 'hadoop-plugin.joined')
@when_not('resourcemanager.ready')
def clear_yarn_ready(client):
    client.clear_yarn_ready()


@when('hadoop.installed')
@when_none('namenode.spec.mismatch', 'resourcemanager.spec.mismatch')
def update_status():
    hdfs_rel = is_state('namenode.joined')
    yarn_rel = is_state('resourcemanager.joined')
    hdfs_ready = is_state('namenode.ready')
    yarn_ready = is_state('resourcemanager.ready')

    if not (hdfs_rel or yarn_rel):
        status_set('blocked',
                   'Waiting for relation to ResourceManager and/or NameNode')
    elif hdfs_rel and not hdfs_ready:
        status_set('waiting', 'Waiting for HDFS')
    elif yarn_rel and not yarn_ready:
        status_set('waiting', 'Waiting for YARN')
    else:
        ready = []
        if hdfs_ready:
            ready.append('HDFS')
        if yarn_ready:
            ready.append('YARN')
        status_set('active', 'Ready ({})'.format(' & '.join(ready)))
