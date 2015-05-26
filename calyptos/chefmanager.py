import glob
from fabric.contrib.project import rsync_project
import json
from os.path import splitext
import os

from fabric.api import *
from fabric.colors import *


def error(message):
    print red(message)
    exit(1)


def info(message):
    print green(message)


def action(message):
    print cyan(message)


class FailedToFindNodeException(Exception):
    pass


class ChefManager():
    CHEF_VERSION = "11.16.4"

    def __init__(self, password, environment_name, hosts, debug=False):
        env.password = password
        env.user = 'root'
        env.parallel = True
        env.pool_size = 20
        env.disable_known_hosts = True
        self.environment_name = environment_name
        self.current_path, self.folder_name = os.path.split(os.getcwd())
        self.remote_folder_path = '/root/' + self.folder_name + '/'
        self.ssh_opts = "-o StrictHostKeyChecking=no"
        self.node_hash = {}
        self.hidden_outputs = ['running', 'stdout', 'stderr']
        with hide(*self.hidden_outputs):
            self.local_hostname = local('hostname', capture=True)
            self.remote_hostnames = execute(run, 'hostname', hosts=hosts)

    @staticmethod
    def sync_ssh_key(hosts, debug=False):
        info('Syncing SSH keys with system under deployment')
        if debug:
            hidden_outputs = []
        else:
            hidden_outputs = ['running', 'stdout', 'stderr']
        with hide(*hidden_outputs):
            pub_key = local('cat ' + os.path.expanduser("~/.ssh/id_rsa.pub"),
                            capture=True)
            cmd = ("yum install rsync -y --nogpg;"
                   "mkdir -p /root/.ssh;"
                   "chmod 0600 /root/.ssh;"
                   "touch /root/.ssh/authorized_keys;"
                   "chmod 0644 /root/.ssh/authorized_keys;"
                   "grep '{0}' /root/.ssh/authorized_keys || echo '{0}' >> /root/.ssh/authorized_keys".format(pub_key))
            info('Running command: {0}'.format(cmd))
            execute(run, cmd, hosts=hosts)

    @staticmethod
    def create_chef_repo(debug=False):
        info('Creating Chef repository')
        if debug:
            hidden_outputs = []
        else:
            hidden_outputs = ['running', 'stdout', 'stderr']
        with hide(*hidden_outputs):
            local('chef generate app chef-repo')
            local('mkdir -p chef-repo/environments')
            local('mkdir -p chef-repo/nodes')

    @staticmethod
    def download_cookbooks(berksfile, cookbook_path='chef-repo/cookbooks',
                           debug=False):
        info('Downloading Chef cookbooks')
        if debug:
            hidden_outputs = []
        else:
            hidden_outputs = ['running', 'stdout', 'stderr']
        with hide(*hidden_outputs):
            local('rm -rf {0}'.format(cookbook_path))
            local('berks vendor --berksfile {0} {1}'.format(berksfile,
                                                            cookbook_path))

    def load_local_node_info(self, chef_repo_dir='chef-repo/'):
        for node_file in glob.glob(chef_repo_dir + 'nodes/*.json'):
            self.read_node_hash(node_file)

    def read_node_hash(self, node_file):
        with open(node_file) as handle:
            data = handle.read()
            node_name = splitext(node_file.split('/')[-1])[0]
            try:
                self.node_hash[node_name] = json.loads(data)
            except ValueError, e:
                print 'Unable to read: ' + node_name
                raise e

    def write_node_hash(self, node_name, chef_repo_dir='chef-repo/'):
        node_json = chef_repo_dir + 'nodes/' + node_name + '.json'
        node_info = json.dumps(self.node_hash[node_name], indent=4,
                               sort_keys=True, separators=(',', ': '))
        with open(node_json, 'w') as env_json:
            env_json.write(node_info)

    def get_node_name_by_ip(self, target_address):
        for node, node_info in self.node_hash.iteritems():
            #ipaddress = node_info['automatic']['ipaddress']
            if target_address in self.get_node_address_list(node_info):
                return node_info['name']
        raise FailedToFindNodeException("Unable to find node: " +
                                        target_address)

    def get_node_address_list(self, node_info):
        auto = node_info['automatic']
        addrs = [auto['ipaddress']]
        network = auto.get('network')
        if network:
            interfaces = network.get('interfaces')
            for interface, i_info  in  interfaces.iteritems():
                for address in i_info.get('addresses', {}):
                    addrs.append(address)
        return addrs

    def add_to_run_list(self, hosts, recipe_list):
        for node_ip in hosts:
            self.load_local_node_info()
            try:
                node_name = self.get_node_name_by_ip(node_ip)
            except FailedToFindNodeException:
                print yellow("Doing initial bootstrap of " + node_ip)
                execute(self.push_deployment_data, hosts=hosts)
                execute(self.run_chef_client, hosts=hosts)
                node_name = self.get_node_name_by_ip(node_ip)
            for recipe in recipe_list:
                if 'run_list' not in self.node_hash[node_name]:
                    # Create empty run_list if it doesnt exist
                    self.node_hash[node_name]['run_list'] = []
                if recipe not in self.node_hash[node_name]['run_list']:
                    self.node_hash[node_name]['run_list'].append(recipe)
            self.write_node_hash(node_name)

    def clear_run_list(self, hosts):
        self.load_local_node_info()
        for node_ip in hosts:
            try:
                node_name = self.get_node_name_by_ip(node_ip)
            except FailedToFindNodeException:
                info('Unable to find node:' + node_ip)
                continue
            self.node_hash[node_name]['run_list'] = []
            self.write_node_hash(node_name)

    def bootstrap_chef(self):
        result = run('chef-client -v', warn_only=True)
        if result.return_code != 0:
            info("Installing chef client on: " + str(env.host))
            run('curl --insecure -L https://www.chef.io/chef/install.sh | '
                'sudo bash -s -- -v ' + self.CHEF_VERSION)

    def run_chef_client(self, chef_command="chef-client -z"):
        with cd(self.remote_folder_path + 'chef-repo'):
            with hide('running'):
                run(chef_command + " -E " + self.environment_name)

    def push_deployment_data(self):
        with hide(*self.hidden_outputs):
            info("rsyncing deployment data...")
            rsync_project(local_dir='./',
                    remote_dir=self.remote_folder_path,
                    ssh_opts=self.ssh_opts, delete=True)

    def pull_node_info(self):
        local_path = 'chef-repo/nodes/' + run('hostname') + '.json'
        remote_path = self.remote_folder_path + local_path
        if self.local_hostname != run('hostname'):
            get(remote_path=remote_path, local_path=local_path)
            self.read_node_hash(local_path)
