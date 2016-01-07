# pylint: disable=unused-argument
from charms.reactive import when, when_not, when_none, is_state
from charmhelpers.core.hookenv import status_set
from charms.hadoop import get_dist_config


@when('hadoop.installed', 'client.related')
def set_installed(client):
    dist = get_dist_config()
    client.set_installed(dist.hadoop_version)


@when('hadoop.installed', 'client.related')
@when('hadoop.hdfs.configured', 'hdfs.ready')
def set_hdfs_ready(hdfs, client):
    client.set_hdfs_ready(hdfs.host(), hdfs.port())


@when('hadoop.installed', 'client.related')
@when_not('hdfs.ready')
def clear_hdfs_ready(client):
    client.clear_hdfs_ready()


@when('hadoop.installed', 'client.related')
@when('hadoop.yarn.configured', 'yarn.ready')
def set_yarn_ready(yarn, client):
    client.set_yarn_ready(yarn.host(), yarn.port(), yarn.hs_http(), yarn.hs_ipc())


@when('hadoop.installed', 'client.related')
@when_not('yarn.ready')
def clear_yarn_ready(client):
    client.clear_yarn_ready()


@when('hadoop.installed')
@when_none('hdfs.spec.mismatch', 'yarn.spec.mismatch')
def update_status():
    hdfs_rel = is_state('hdfs.related')
    yarn_rel = is_state('yarn.related')
    hdfs_ready = is_state('hdfs.ready')
    yarn_ready = is_state('yarn.ready')

    if not (hdfs_rel or yarn_rel):
        status_set('blocked', 'Waiting for relation to ResourceManager and/or NameNode')
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
