# Fablib gluster

This is fablib for gluster.


## Example vars
``` bash
node_map:
  gluster:
    hosts:
      - dev01.mydns.jp
      - dev02.mydns.jp
    fabruns:
      - openstack/gluster

gluster:
  common:
    volume: common
    brick: /export/common
    hosts: ${#node_map.gluster.hosts}
    host: ${#node_map.gluster.hosts.0}
```

## Example fabscript
``` python
# coding: utf-8

from fabkit import task, api
from fablib.gluster import Gluster

gluster = Gluster()


@task
def setup0():
    gluster.setup()


@task
@api.serial
def setup1_peer():
    gluster.setup_peer()


@task
def setup2_volume():
    gluster.setup_volume()
```
