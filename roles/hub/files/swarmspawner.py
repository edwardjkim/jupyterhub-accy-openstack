import os
import stat
from tornado import gen
from dockerspawner import DockerSpawner
from traitlets import Unicode

# urllib3 complains that we're making unverified HTTPS connections to swarm,
# but this is ok because we're connecting to swarm via 127.0.0.1. I don't
# actually want swarm listening on a public port, so I don't want to connect
# to swarm via the host's FQDN, which means we can't do fully verified HTTPS
# connections. To prevent the warning from appearing over and over and over
# again, I'm just disabling it for now.
import requests
requests.packages.urllib3.disable_warnings()


class SwarmSpawner(DockerSpawner):

    container_ip = '0.0.0.0'

    singleuser = Unicode('jovyan', config=True)

    hostname = Unicode('jupyter', config=True)

    root_dir = Unicode('/export', config=True)

    course_id = Unicode('accy', config=True)

    @gen.coroutine
    def lookup_node_name(self):
        """Find the name of the swarm node that the container is running on."""
        containers = yield self.docker('containers', all=True)
        for container in containers:
            if container['Id'] == self.container_id:
                name, = container['Names']
                node, container_name = name.lstrip("/").split("/")
                raise gen.Return(node)

    @gen.coroutine
    def start(self, image=None, extra_create_kwargs=None, extra_host_config=None):
        # look up mapping of node names to ip addresses
        info = yield self.docker('info')
        num_nodes = int(info['SystemStatus'][3][1])
        node_info = info['SystemStatus'][4::9]
        self.node_info = {}
        for i in range(num_nodes):
            node, ip_port = node_info[i]
            self.node_info[node.strip()] = ip_port.strip().split(":")[0]
        self.log.debug("Swarm nodes are: {}".format(self.node_info))

        # specify extra host configuration
        if extra_host_config is None:
            extra_host_config = {}
        if 'mem_limit' not in extra_host_config:
            extra_host_config['mem_limit'] = '1g'

        # specify extra creation options
        if extra_create_kwargs is None:
            extra_create_kwargs = {}
        if 'working_dir' not in extra_create_kwargs:
            extra_create_kwargs['working_dir'] = "/home/{}".format(self.singleuser)
        if 'hostname' not in extra_create_kwargs:
            extra_create_kwargs['hostname'] = self.hostname

        # create and set permissions of home dir if it doesn't exist
        home_dir = os.path.join(self.root_dir, 'home', self.user.name)
        if not os.path.exists(home_dir):
            os.makedirs(home_dir)
            os.chown(home_dir, 1000, 100)

        exchange_dir = os.path.join(
            self.root_dir, 'exchange', self.user.name, self.course_id
        )
        if not os.path.exists(exchange_dir):
            os.makedirs(exchange_dir)
        os.chown(exchange_dir, 1000, 100)

        inbound_dir = os.path.join(
            self.root_dir, 'exchange', self.user.name, self.course_id, 'inbound'
        )
        if not os.path.exists(inbound_dir):
            os.makedirs(inbound_dir)
        os.chown(inbound_dir, 0, 0)
        os.chmod(
            inbound_dir,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IWGRP | stat.S_IXGRP | stat.S_IWOTH | stat.S_IXOTH
        )

        outbound_dir = os.path.join(
            self.root_dir, 'exchange', self.user.name, self.course_id, 'outbound'
        )
        if not os.path.exists(outbound_dir):
            os.makedirs(outbound_dir)
        os.chown(inbound_dir, 0, 0)
        os.chmod(
            outbound_dir,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
        )

        # start the container
        yield DockerSpawner.start(
            self, image=image,
            extra_create_kwargs=extra_create_kwargs,
            extra_host_config=extra_host_config)

        # figure out what the node is and then get its ip
        name = yield self.lookup_node_name()
        self.user.server.ip = self.node_info[name]
        self.log.info("{} was started on {} ({}:{})".format(
            self.container_name, name, self.user.server.ip, self.user.server.port))

        self.log.info(self.env)
