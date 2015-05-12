import yaml


class ComponentDeployer():
    def __init__(self, environment_file='environment.yml'):
        self.environment_file = environment_file
        self.roles = self.get_roles()
        self.all_hosts = self.roles['all']

    def read_environment(self):
        return yaml.load(open(self.environment_file).read())

    def get_euca_attributes(self):
        env_dict = self.read_environment()
        return env_dict['default_attributes']['eucalyptus']

    def get_roles(self):
        euca_attributes = self.get_euca_attributes()
        topology = euca_attributes['topology']
        if 'clc-1' not in topology:
            raise IndexError("Unable to find CLC in topology")
        roles = {'clc': set([topology['clc-1']]),
                 'user-facing': set(topology['user-facing']),
                 'cluster-controller': set(), 'storage-controller': set(),
                 'node-controller': set(), 'vmware-broker': set(), 'nuke': set(),
                 'midolman': set(), 'midonet-gw': set(),
                 'all': set([topology['clc-1']])
                 }
        for ufs in topology['user-facing']:
            roles['all'].add(ufs)
        if 'walrus' in topology:
            roles['walrus'] = set([topology['walrus']])
            roles['all'].add(topology['walrus'])
        else:
            # No walrus defined assuming RiakCS
            roles['walrus'] = set()
        for name in topology['clusters']:
            roles['cluster'] = {}
            if 'cc-1' in topology['clusters'][name]:
                cc = topology['clusters'][name]['cc-1']
                roles['cluster-controller'].add(cc)
            else:
                raise IndexError("Unable to find CC in topology for cluster " + name)

            if 'sc-1' in topology['clusters'][name]:
                sc = topology['clusters'][name]['sc-1']
                roles['storage-controller'].add(sc)
            else:
                raise IndexError("Unable to find SC in topology for cluster " + name)

            roles['cluster'][name] = set([cc, sc])
            if 'nodes' in topology['clusters'][name]:
                nodes = topology['clusters'][name]['nodes'].split()
            else:
                raise IndexError("Unable to find nodes in topology for cluster " + name)
            for node in nodes:
                roles['node-controller'].add(node)
                roles['cluster'][name].add(node)
            roles['all'].update(roles['cluster'][name])
        if euca_attributes['network']['mode'] == 'VPCMIDO':
            roles['midolman'] = roles['node-controller']
            roles['midonet-gw'] = roles['clc']
        return roles
