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

    def __init__(self, password, environment_name, hosts):
        env.password = password
        env.user = 'root'
        env.parallel = True
        env.pool_size = 20
        self.environment_name = environment_name
        self.current_path, self.folder_name = os.path.split(os.getcwd())
        self.remote_folder_path = '/root/' + self.folder_name + '/'
        self.ssh_opts = "-o StrictHostKeyChecking=no"
        self.local_hostname = local('hostname', capture=True)
        self.node_hash = {}
        self.remote_hostnames = execute(run, 'hostname', hosts=hosts)

    @staticmethod
    def sync_ssh_key(hosts):
        pub_key = local('cat ' + os.path.expanduser("~/.ssh/id_rsa.pub"),
                        capture=True)
        execute(run, "echo '" + pub_key + "' >> /root/.ssh/authorized_keys",
                hosts=hosts)

    @staticmethod
    def download_cookbook_deps():
        local('chef generate chef-repo')
        local('mkdir -p chef-repo/environments')
        local('mkdir -p chef-repo/nodes')
        local('git clone https://github.com/eucalyptus/eucalyptus-cookbook')
        local('berks vendor --berksfile eucalyptus-cookbook/Berksfile '
              'chef-repo/cookbooks')

    def load_local_node_info(self, chef_repo_dir='chef-repo/'):
        for node_file in glob.glob(chef_repo_dir + 'nodes/*.json'):
            self.read_node_hash(node_file)

    def read_node_hash(self, node_file):
        with open(node_file) as handle:
            data = handle.read()
            node_name = splitext(node_file.split('/')[-1])[0]
            self.node_hash[node_name] = json.loads(data)

    def write_node_hash(self, node_name, chef_repo_dir='chef-repo/'):
        node_json = chef_repo_dir + 'nodes/' + node_name + '.json'
        node_info = json.dumps(self.node_hash[node_name], indent=4,
                               sort_keys=True, separators=(',', ': '))
        info('Writing out node: ' + node_json)
        with open(node_json, 'w') as env_json:
            env_json.write(node_info)

    def get_node_name_by_ip(self, target_address):
        for node, node_info in self.node_hash.iteritems():
            nics = node_info['automatic']['network']['interfaces']
            for interface, if_info in nics.iteritems():
                for address in if_info['addresses']:
                    if target_address == address:
                        return node_info['name']
        raise FailedToFindNodeException("Unable to find node: " +
                                        target_address)

    def add_to_run_list(self, hosts, recipe_list):
        for node_ip in hosts:
            self.load_local_node_info()
            try:
                node_name = self.get_node_name_by_ip(node_ip)
            except FailedToFindNodeException:
                print yellow("Doing initial bootstrap of " + node_ip)
                self.run_chef_client(hosts=hosts)
                node_name = self.get_node_name_by_ip(node_ip)
            for recipe in recipe_list:
                if 'run_list' not in self.node_hash[node_name]:
                    # Create empty run_list if it doesnt exist
                    self.node_hash[node_name]['run_list'] = []
                if recipe not in self.node_hash[node_name]['run_list']:
                    self.node_hash[node_name]['run_list'].append(recipe)
            self.write_node_hash(node_name)

    def clear_run_list(self, hosts):
        for node_ip in hosts:
            try:
                node_name = self.get_node_name_by_ip(node_ip)
            except FailedToFindNodeException:
                continue
            self.node_hash[node_name]['run_list'] = []
            self.write_node_hash(node_name)

    def bootstrap_chef(self, hosts):
        results = execute(run, 'chef-client -v', warn_only=True, hosts=hosts)
        install_hosts = hosts
        for host in results.keys():
            if 'Chef' in results[host]:
                install_hosts.remove(host)
        if install_hosts:
            info("Installing chef client on: " + str(hosts) + str(results))
            execute(run,
                    'curl -L https://www.chef.io/chef/install.sh | '
                    'sudo bash -s -- -v ' + self.CHEF_VERSION,
                    hosts=install_hosts)

    def run_chef_client(self, hosts, chef_command="chef-client -z"):
        # self.bootstrap_chef(hosts)
        info("Running chef client run on: " + str(hosts))
        with cd(self.remote_folder_path + 'chef-repo'):
            execute(run, chef_command + " -E " + self.environment_name,
                    hosts=hosts)

    def push_deployment_data(self, hosts):
        info('Pushing data to: ' + str(hosts))
        execute(rsync_project, local_dir='./',
                remote_dir=self.remote_folder_path,
                ssh_opts=self.ssh_opts, delete=True, hosts=hosts)

    def pull_node_info(self):
        for host in self.remote_hostnames:
            local_path = 'chef-repo/nodes/' + \
                         self.remote_hostnames[host] + '.json'
            remote_path = self.remote_folder_path + local_path
            execute(get, remote_path=remote_path,
                    local_path=local_path, hosts=[host])
            self.read_node_hash(local_path)
