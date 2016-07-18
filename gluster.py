# coding: utf-8

from fabkit import filer, sudo, env, Service
from fablib.base import SimpleBase


class Gluster(SimpleBase):
    def __init__(self):
        self.data_key = 'gluster'
        self.data = {
        }

        self.services = {
            'CentOS Linux 7.*': [
                'glusterd',
            ]
        }

        self.packages = {
            'CentOS Linux 7.*': [
                'centos-release-gluster36',
                'glusterfs-server',
                'glusterfs-fuse',
            ]
        }

    def init_after(self):
        for cluster in self.data.get('clusters', {}).values():
            if env.host in cluster['hosts']:
                self.data.update(cluster)

    def setup(self):
        data = self.init()

        Service('firewalld').stop().disable()

        self.install_packages()
        self.start_services().enable_services()

        for volume in data['volume_map'].values():
            filer.mkdir(volume['brick'])

    def setup_peer(self):
        """
        require serial task.
        """

        data = self.init()
        for host in data['hosts']:
            if host != env.host:
                sudo('gluster peer probe {0}'.format(host))

    def setup_volume(self):
        """
        require serial task.
        """

        data = self.init()
        if data['hosts'][0] != env.host:
            return

        for volume in data['volume_map'].values():
            bricks = ''
            replica_option = 'replica 2' if len(data['hosts']) > 1 else ''
            for host in data['hosts']:
                bricks += '{0}:{1} '.format(host, volume['brick'])
            sudo('gluster volume info {0[name]} || gluster volume create '
                 '{0[name]} {1} {2} force'.format(
                     volume, replica_option, bricks))
            sudo('gluster volume info {0[name]} | grep Started'
                 ' || gluster volume start {0[name]}'.format(
                     volume))

    def mount_local(self):
        data = self.init()
        for volume in data['volume_map'].values():
            filer.Editor('/etc/fstab').a('localhost:/{0} /mnt/{0} glusterfs '
                                         'defaults,_netdev 0 0'.format(volume['name']))
            filer.mkdir('/mnt/{0}'.format(volume['name']))
            sudo('mount -a')
