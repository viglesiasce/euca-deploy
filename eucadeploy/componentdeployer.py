import json
import os
from fabric.context_managers import hide
from fabric.operations import local
from fabric.tasks import execute
import yaml
from eucadeploy.chefmanager import ChefManager


class ComponentDeployer():
    def __init__(self, password, environment_file='environment.yml',
                 config_file='config.yml', debug=False,
                 cookbook_branch='euca-4.1',
                 cookbook_repo='https://github.com/eucalyptus/eucalyptus-cookbook'):
        self.environment_file = environment_file
        self.config_file = config_file
        self.config = self.read_config()
        self.chef_repo_dir = 'chef-repo'
        ChefManager.create_chef_repo()
        if debug:
            self.hidden_outputs = []
        else:
            self.hidden_outputs = ['running', 'stdout', 'stderr']
        with hide(*self.hidden_outputs):
            local('if [ ! -d eucalyptus-cookbook ]; then '
                  'git clone '
                  '{0} eucalyptus-cookbook;'
                  'fi'.format(cookbook_repo))
            local('cd eucalyptus-cookbook; git checkout {0};'.format(cookbook_branch))
            local('cd eucalyptus-cookbook; git pull;')
        ChefManager.download_cookbooks('eucalyptus-cookbook/Berksfile',
                                       os.path.join(self.chef_repo_dir +
                                                    '/cookbooks'),
                                       debug=debug)
        self.environment_name = self.write_json_environment()
        self.roles = self.generate_roles()
        self.all_hosts = self.roles['all']
        self.chef_manager = ChefManager(password, self.environment_name,
                                        self.roles['all'])


    def read_config(self):
        return yaml.load(open(self.config_file).read())

    def get_recipe_list(self, component):
        for recipe_dict in self.config['recipes']:
            if recipe_dict.has_key(component):
                return recipe_dict[component]
        raise ValueError('No component found for: ' + component)

    def write_json_environment(self):
        environment_dict = yaml.load(open(self.environment_file).read())
        current_environment = environment_dict['name']
        environment_dir = self.chef_repo_dir + '/environments/'
        filename = environment_dir + current_environment + '.json'
        with open(filename, 'w') as env_json:
            env_json.write(json.dumps(environment_dict, indent=4,
                                      sort_keys=True, separators=(',', ': ')))
        return current_environment

    def _get_environment(self):
        with open(self.chef_repo_dir + '/environments/' +
                self.environment_name + '.json') as env_file:
            return json.loads(env_file.read())

    def _get_euca_attributes(self):
        env_dict = self._get_environment()
        return env_dict['default_attributes']['eucalyptus']

    def generate_roles(self):
        euca_attributes = self._get_euca_attributes()
        topology = euca_attributes['topology']
        roles = {'clc': [topology['clc-1']],
                 'user-facing': topology['user-facing'],
                 'cluster-controller': [], 'storage-controller': [],
                 'node-controller': [], 'vmware-broker': [], 'nuke': [],
                 'midolman': [], 'midonet-gw': [],
                 'all': [topology['clc-1']] + topology['user-facing']}
        if topology.has_key('walrus'):
            roles['walrus']= [topology['walrus']]
            roles['all'].append(topology['walrus'])
        else:
            self.config['recipes'].remove({'walrus': ['eucalyptus::walrus']})
        for name in topology['clusters']:
            cc = topology['clusters'][name]['cc-1']
            sc = topology['clusters'][name]['sc-1']
            if 'vmware-broker' in topology['clusters'][name]:
                vb = topology['clusters'][name]['vmware-broker']
                roles['vmware-broker'].append(vb)
            nodes = topology['clusters'][name]['nodes'].split()
            roles['cluster-controller'].append(cc)
            roles['storage-controller'].append(sc)
            roles['node-controller'] += nodes
            roles['all'] += [cc, sc] + nodes
        if euca_attributes['network']['mode'] == 'VPCMIDO':
            roles['midolman'] = roles['node-controller']
            roles['midonet-gw'] = roles['clc']
        return roles

    def prepare(self):
        self.chef_manager.sync_ssh_key(self.all_hosts)
        self.chef_manager.clear_run_list(self.all_hosts)
        order = [self.chef_manager.push_deployment_data,
                 self.chef_manager.bootstrap_chef,
                 self.chef_manager.run_chef_client,
                 self.chef_manager.pull_node_info]
        for method in order:
            with hide(*self.hidden_outputs):
                execute(method, hosts=self.all_hosts)

    def run_chef_on_hosts(self, hosts):
        with hide(*self.hidden_outputs):
            execute(self.chef_manager.push_deployment_data, hosts=hosts)
        execute(self.chef_manager.run_chef_client, hosts=hosts)
        execute(self.chef_manager.pull_node_info, hosts=hosts)

    def bootstrap(self):
        # Install CLC and Initialize DB
        clc = self.roles['clc']
        self.chef_manager.clear_run_list(self.all_hosts)
        self.chef_manager.add_to_run_list(clc,
                                          self.get_recipe_list('clc'))
        self.run_chef_on_hosts(clc)

    def provision(self):
        # Install all other components and configure CLC
        self.chef_manager.clear_run_list(self.all_hosts)
        for role_dict in self.config['recipes']:
            component_name = role_dict.keys().pop()
            self.chef_manager.add_to_run_list(self.roles[component_name],
                                              self.get_recipe_list(
                                                  component_name))
        self.run_chef_on_hosts(self.all_hosts)
        clc = self.roles['clc']
        self.chef_manager.add_to_run_list(clc, ['eucalyptus::configure'])
        self.run_chef_on_hosts(clc)
        if self._get_euca_attributes()['network']['mode'] == 'VPCMIDO':
            midonet_gw = self.roles['midonet-gw']
            self.chef_manager.add_to_run_list(midonet_gw,
                                              ['midokura::create-first-resources'])
            self.run_chef_on_hosts(midonet_gw)

    def uninstall(self):
        self.chef_manager.clear_run_list(self.all_hosts)
        self.chef_manager.add_to_run_list(self.all_hosts,
                                          self.get_recipe_list('nuke'))
        self.run_chef_on_hosts(self.all_hosts)
        self.chef_manager.clear_run_list(self.all_hosts)

