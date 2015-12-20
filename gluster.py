# coding: utf-8

from fabkit import filer, sudo, env, Service
from fablib.base import SimpleBase


class Gluster(SimpleBase):
    def __init__(self):
        self.data_key = 'gluster'
        self.data = {
        }

        self.services = [
            'glusterd',
        ]

        self.packages = [
            'glusterfs-server',
        ]

    def init_after(self):
        for cluster in self.data.values():
            if env.host in cluster['hosts']:
                self.data['gluster_cluster'] = cluster
                break

    def setup(self):
        data = self.init()
        cluster = data['gluster_cluster']

        filer.template('/etc/yum.repos.d/glusterfs-epel.repo')

        self.install_packages('--enablerepo glusterfs-epel')
        self.start_services().enable_services()

        filer.mkdir(cluster['brick'])

        Service('firewalld').stop().disable()

    def setup_peer(self):
        """
        This method should be called in sirial task
        """
        data = self.init()
        cluster = data['gluster_cluster']

        for host in cluster['hosts']:
            if host != env.host:
                sudo('gluster peer probe {0}'.format(host))

    def setup_volume(self):
        data = self.init()
        cluster = data['gluster_cluster']
        if cluster['hosts'][0] != env.host:
            return

        sudo('gluster volume info {0} || gluster volume create '
             '{0} replica 2 {1}:{2} {3}:{2} force'.format(
                 cluster['volume'], cluster['hosts'][0], cluster['brick'], cluster['hosts'][1]))
        sudo('gluster volume info {0} | grep Started || gluster volume start {0}'.format(
            cluster['volume']))
