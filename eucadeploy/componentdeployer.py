import json
from fabric.colors import *
import yaml
from eucadeploy.chefmanager import ChefManager


def error(message):
    print red(message)
    exit(1)


def info(message):
    print green(message)


def action(message):
    print cyan(message)


class ComponentDeployer():
    def __init__(self, password, environment_file='environment.yml',
                 config_file='config.yml'):
        self.environment_file = environment_file
        self.config_file = config_file
        self.config = self.read_config()
        self.chef_repo_dir = 'chef-repo'
        self.environment_name = self.write_json_environment()
        self.roles = self.generate_roles()
        self.all_hosts = self.roles['all']
        self.chef_manager = ChefManager(password, self.environment_name,
                                        self.roles['all'])

    def read_config(self):
        info("Reading deployment configuration")
        return yaml.load(open(self.config_file).read())

    def write_json_environment(self):
        info("Translating config from YAML to JSON")
        environment_dict = yaml.load(open(self.environment_file).read())
        current_environment = environment_dict['name']
        environment_dir = self.chef_repo_dir + '/environments/'
        filename = environment_dir + current_environment + '.json'
        with open(filename, 'w') as env_json:
            env_json.write(json.dumps(environment_dict, indent=4,
                                      sort_keys=True, separators=(',', ': ')))
        return current_environment

    def generate_roles(self):
        roles = {}
        with open(self.chef_repo_dir + '/environments/' +
                  self.environment_name + '.json') as env_file:
            env_dict = json.loads(env_file.read())
            euca_attributes = env_dict['default_attributes']['eucalyptus']
            topology = euca_attributes['topology']
        roles['clc'] = [topology['clc-1']]
        roles['walrus'] = [topology['walrus']]
        roles['user-facing'] = topology['user-facing']
        roles['cluster-controller'] = []
        roles['storage-controller'] = []
        roles['node-controller'] = []
        roles['nuke'] = []
        roles['midolman'] = []
        roles['midonet-gw'] = []
        roles['configure'] = roles['clc']
        roles['all'] = [topology['clc-1'],
                        topology['walrus']] + topology['user-facing']
        for name in topology['clusters']:
            cc = topology['clusters'][name]['cc-1']
            sc = topology['clusters'][name]['sc-1']
            nodes = topology['clusters'][name]['nodes'].split()
            roles['cluster-controller'].append(cc)
            roles['storage-controller'].append(sc)
            roles['node-controller'] += nodes
            roles['all'] += [cc, sc] + nodes
        return roles

    def prepare_systems(self):
        self.chef_manager.sync_ssh_key(self.all_hosts)
        self.chef_manager.push_deployment_data(self.all_hosts)
        self.chef_manager.run_chef_client(self.all_hosts)
        self.chef_manager.pull_node_info()

    def install(self):
        self.prepare_systems()

        # Install CLC and Initialize DB
        self.chef_manager.add_to_run_list(self.roles['clc'],
                                          self.config['recipes']['clc'])
        self.chef_manager.push_deployment_data(self.all_hosts)
        self.chef_manager.run_chef_client(self.all_hosts)
        self.chef_manager.pull_node_info()

        # Install all other components and configure CLC
        for role in self.config['recipes']:
            self.chef_manager.add_to_run_list(self.roles[role],
                                              self.config['recipes'][role])
        self.chef_manager.push_deployment_data(self.all_hosts)
        self.chef_manager.run_chef_client(self.all_hosts)
        self.chef_manager.pull_node_info()

    def uninstall(self):
        self.prepare_systems()
        self.chef_manager.clear_run_list(self.all_hosts)
        self.chef_manager.add_to_run_list(self.all_hosts,
                                          self.config['recipes']['nuke'])
        self.chef_manager.run_chef_client(self.all_hosts)
        self.chef_manager.clear_run_list(self.all_hosts)
