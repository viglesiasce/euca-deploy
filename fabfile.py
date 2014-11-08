import glob
import json
from os.path import splitext
import os

from fabric.api import *
from fabric.colors import *
from fabric.state import output
import yaml

env.user = 'root'
env.pool_size = 72


node_hash = {}
output['stdout'] = True
output['status'] = True
output['running'] = True


__all__ = ['full_install', 'push_configuration', 'clc', 'frontends', 'midtier',
           'nodes', 'configure', 'midolmen', 'midonet_gw', 'sync_ssh_key', 'uninstall']

class FailedToFindNodeException(Exception):
    pass

def error(message):
    print red(message)
    exit(1)


def info(message):
    print green(message)


def action(message):
    print cyan(message)


def translate_config(chef_repo_dir='chef-repo'):
    config_dict = yaml.load(open('config.yml').read())
    current_environment = config_dict['name']
    filename = chef_repo_dir + '/environments/' + current_environment + '.json'
    with open(filename, 'w') as env_json:
        env_json.write(json.dumps(config_dict, indent=4, sort_keys=True, separators=(',', ': ')))
    return current_environment


def compile_fabric_roles(current_environment, chef_repo_dir='chef-repo'):
    with open(chef_repo_dir + '/environments/' + current_environment + '.json') as env_file:
        env.topology = json.loads(env_file.read())['default_attributes']['eucalyptus']['topology']
    env.roledefs['clc'] = [env.topology['clc-1']]
    env.roledefs['frontends'] = [env.topology['walrus']] + env.topology['user-facing']
    env.roledefs['midtier'] = []
    env.roledefs['nodes'] = []
    for name in env.topology['clusters']:
        env.roledefs['midtier'] += [env.topology['clusters'][name]['cc-1'], env.topology['clusters'][name]['sc-1']]
        env.roledefs['nodes'] += env.topology['clusters'][name]['nodes'].split()
    env.roledefs['all'] = env.roledefs['clc'] + env.roledefs['frontends'] + env.roledefs['midtier'] + env.roledefs[
        'nodes']


environment_name = translate_config()
compile_fabric_roles(environment_name)

def load_local_node_info(chef_repo_dir='chef-repo/'):
    for node_file in glob.glob(chef_repo_dir + 'nodes/*.json'):
        read_node_hash(node_file)

def read_node_hash(node_file):
    with open(node_file) as handle:
        try:
            data = handle.read()
            node_hash[splitext(node_file.split('/')[-1])[0]] = json.loads(data)
        except ValueError, e:
            pass

@task
@serial
def write_node_hash(node_name, chef_repo_dir='chef-repo/'):
    node_json = chef_repo_dir + 'nodes/' + node_name + '.json'
    with open(node_json, 'w') as env_json:
        env_json.write(json.dumps(node_hash[node_name], indent=4, sort_keys=True, separators=(',', ': ')))


def get_node_name_by_ip(target_address):
    load_local_node_info()
    for node, node_info in node_hash.iteritems():
        for interface, if_info in node_info['automatic']['network']['interfaces'].iteritems():
            for address in if_info['addresses']:
                if target_address == address:
                    return node_info['name']
    raise FailedToFindNodeException("Unable to find node: " + target_address)


@task
def add_to_run_list(node_ip, recipe_list):
    try:
        node_name = get_node_name_by_ip(node_ip)
    except FailedToFindNodeException:
        print yellow("Doing initial bootstrap of " + env.host_string)
        execute(run_chef_client)
        node_name = get_node_name_by_ip(node_ip)
    for recipe in recipe_list:
        if 'run_list' not in node_hash[node_name]:
            ### Create empty run_list if it doesnt exist
            node_hash[node_name]['run_list'] = []
        if recipe not in node_hash[node_name]['run_list']:
            node_hash[node_name]['run_list'].append(recipe)
    execute(write_node_hash, node_name)
    if local('hostname', capture=True) != node_name:
        push_configuration()
    run_chef_client()


@task
def clear_run_list(node_ip):
    try:
        node_name = get_node_name_by_ip(node_ip)
    except FailedToFindNodeException:
        return
    node_hash[node_name]['run_list'] = []
    execute(write_node_hash, node_name)


@task
@runs_once
def create_repo_tarball(chef_repo_dir='chef-repo/'):
    print yellow("Pushing deployment files to: " + env.host_string)
    chef_repo_tarball = 'chef-repo.tgz'
    local('tar zcvf ' + chef_repo_tarball + ' ' + chef_repo_dir)


@roles('all')
@task
@parallel
def push_configuration(remote_chef_tarball_path="/root/euca-deploy/", chef_repo_dir='chef-repo/'):
    """Push deployment data from localhost to Eucalyptus Machines"""
    if local('hostname', capture=True) != run('hostname'):
        chef_repo_tarball = 'chef-repo.tgz'
        with hide("everything"):
            execute(create_repo_tarball)
            run('rm -rf ' + remote_chef_tarball_path + 'chef-repo')
            run('mkdir -p ' + remote_chef_tarball_path)
            put(chef_repo_tarball, remote_path=remote_chef_tarball_path)
            with cd(remote_chef_tarball_path):
                run('tar xzfv ' + chef_repo_tarball)


@task
def bootstrap_chef():
    result = run('chef-client -v', warn_only=True)
    if result.return_code != 0:
        run('curl -L https://www.opscode.com/chef/install.sh | bash')


@task
@parallel
def run_chef_client(repo_path="/root/euca-deploy/chef-repo/", chef_command="chef-client -z", options=""):
    with cd(repo_path):
        execute(bootstrap_chef)
        run("hostname && " + chef_command + " " + options + " -E " + environment_name)
    info("Completed deployment on: " + env.host_string)
    hostname = run('hostname')
    node_file = repo_path + 'nodes/' + hostname + '.json'
    ### Dont download if we are local
    if local('hostname', capture=True, ) != hostname:
        get(remote_path=node_file, local_path=node_file)
    read_node_hash(node_file)


@roles('clc')
@task
def clc():
    """Deploy CLC and register components"""
    action("Deploying CLC: " + env.host_string)
    add_to_run_list(env.host_string,
                    ['recipe[eucalyptus::cloud-controller]', 'recipe[eucalyptus::register-components]'])


@roles('frontends')
@task
@parallel
def frontends():
    """Deploy Walrus and User Facing Services"""
    action("Deploying Walrus and User Facing Service: " + env.host_string)
    add_to_run_list(env.host_string, ['recipe[eucalyptus::cloud-service]', 'recipe[eucalyptus::walrus]'])


@roles('midtier')
@task()
@parallel()
def midtier():
    """Deploy Cluster and Storage Controllers"""
    action("Deploying Cluster and Storage Controller: " + env.host_string)
    add_to_run_list(env.host_string,
                    ['recipe[eucalyptus::cluster-controller]', 'recipe[eucalyptus::storage-controller]'])


@roles('nodes')
@task
@parallel
def nodes():
    """Deploy Node Controllers"""
    action("Deploying Node Controller: " + env.host_string)
    add_to_run_list(env.host_string, ['recipe[eucalyptus::node-controller]'])


@roles('nodes')
@task
@parallel
def midolmen():
    """Install Midokura on Node Controllers"""
    action("Deploying Midolman Node Controller: " + env.host_string)
    add_to_run_list(env.host_string, ['recipe[midokura::midolman]'])


@roles('clc')
@task
@parallel
def midonet_gw():
    """Install Midokura GW"""
    action("Deploying Midokura API/GW on CLC: " + env.host_string)
    add_to_run_list(env.host_string, ['recipe[midokura]'])



@roles('clc')
@task
def configure():
    """Run configuration step on CLC"""
    action("Doing final configuration on CLC: " + env.host_string)
    add_to_run_list(env.host_string, ['recipe[eucalyptus::configure]'])


@task
def stack_order(stack_order):
    for method in stack_order:
        execute(push_configuration)
        execute(method)

@roles('all')
@task
def sync_ssh_key():
    pub_key = local('cat ' + os.path.expanduser("~/.ssh/id_rsa.pub"), capture=True)
    run("echo '" + pub_key + "' >> /root/.ssh/authorized_keys")


@task
def full_install():
    """End to end Eucalyptus installation"""
    execute(stack_order, [clc, frontends, midtier, nodes, configure])


@task
def uninstall():
    execute(stack_order, [nuke])


@roles('all')
@task
def nuke():
    action("Wiping Eucalyptus off machine: " + env.host_string)
    run('yum clean metadata')
    clear_run_list(env.host_string)
    add_to_run_list(env.host_string, ['recipe[eucalyptus::nuke]'])
    clear_run_list(env.host_string)
