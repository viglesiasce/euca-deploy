import json
from fabric.operations import local
import yaml
from deployerplugin import DeployerPlugin
from fabric.context_managers import hide
from fabric.tasks import execute
from calyptos.chefmanager import ChefManager
import os
from calyptos.componentdeployer import ComponentDeployer


class Chef(DeployerPlugin):
    def __init__(self, password, environment_file='etc/environment.yml',
                 config_file='config.yml', debug=False, branch='euca-4.1',
                 repo='https://github.com/eucalyptus/eucalyptus-cookbook'):
        self.chef_repo_dir = 'chef-repo'
        self.environment_file = environment_file
        if debug:
            self.hidden_outputs = []
        else:
            self.hidden_outputs = ['running', 'stdout', 'stderr']
        self.component_deployer = ComponentDeployer(environment_file)
        self.roles = self.component_deployer.get_roles()
        self.all_hosts = self.roles['all']
        self.environment_name = self._write_json_environment()
        self._prepare_fs(repo, branch, debug)
        self.chef_manager = ChefManager(password, self.environment_name,
                                        self.roles['all'])
        self.config_file = config_file
        self.config = self.read_config()

    def _prepare_fs(self, repo, branch, debug):
        ChefManager.create_chef_repo()
        with hide(*self.hidden_outputs):
            local('if [ ! -d eucalyptus-cookbook ]; then '
                  'git clone '
                  '{0} eucalyptus-cookbook;'
                  'fi'.format(repo))
            local('cd eucalyptus-cookbook; git checkout {0};'.format(branch))
            local('cd eucalyptus-cookbook; git pull;')
        ChefManager.download_cookbooks('eucalyptus-cookbook/Berksfile',
                                       os.path.join(self.chef_repo_dir +
                                                    '/cookbooks'),
                                       debug=debug)

    def read_config(self):
        return yaml.load(open(self.config_file).read())

    def _get_recipe_list(self, component):
        for recipe_dict in self.config['recipes']:
            if component in recipe_dict:
                return recipe_dict[component]
        raise ValueError('No component found for: ' + component)

    def _write_json_environment(self):
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

    def _run_chef_on_hosts(self, hosts):
        with hide(*self.hidden_outputs):
            execute(self.chef_manager.push_deployment_data, hosts=hosts)
        execute(self.chef_manager.run_chef_client, hosts=hosts)
        execute(self.chef_manager.pull_node_info, hosts=hosts)

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

    def bootstrap(self):
        # Install CLC and Initialize DB
        clc = self.roles['clc']
        self.chef_manager.clear_run_list(self.all_hosts)
        self.chef_manager.add_to_run_list(clc,
                                          self._get_recipe_list('clc'))
        self._run_chef_on_hosts(clc)

    def provision(self):
        # Install all other components and configure CLC
        self.chef_manager.clear_run_list(self.all_hosts)
        for role_dict in self.config['recipes']:
            component_name = role_dict.keys().pop()
            self.chef_manager.add_to_run_list(self.roles[component_name],
                                              self._get_recipe_list(
                                                  component_name))
        self._run_chef_on_hosts(self.all_hosts)
        clc = self.roles['clc']
        self.chef_manager.add_to_run_list(clc, ['eucalyptus::configure'])
        self._run_chef_on_hosts(clc)
        if self.component_deployer.get_euca_attributes()['network']['mode'] == 'VPCMIDO':
            midonet_gw = self.roles['midonet-gw']
            create_resources = 'midokura::create-first-resources'
            self.chef_manager.add_to_run_list(midonet_gw,
                                              [create_resources])
            self._run_chef_on_hosts(midonet_gw)

    def uninstall(self):
        self.chef_manager.clear_run_list(self.all_hosts)
        self.chef_manager.add_to_run_list(self.all_hosts,
                                          self._get_recipe_list('nuke'))
        self._run_chef_on_hosts(self.all_hosts)
        self.chef_manager.clear_run_list(self.all_hosts)