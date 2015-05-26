from calyptos.plugins.validator.validatorplugin import ValidatorPlugin
from schema import Schema, And, Or, Use, Optional

class Structure(ValidatorPlugin):
    def validate(self):
        self.envdata = self.environment
        self.schema = Schema(
            {
                'description': And(str, error="Invalid environment.yml value(s) for 'description'."),
                'name': And(str, error="Invalid environment.yml value(s) for 'name'."),
                Optional('cookbook_versions'):
                    And(dict, error="Invalid environment.yml value(s) for 'cookbook_versions'."),
                Optional('override_attributes'):
                    And(dict, error="Invalid environment.yml value(s) for 'override_attributes'."),
                'default_attributes':
                    {
                        'eucalyptus':
                            {
                                'network':
                                    {
                                        'mode': And(str, error="Invalid environment.yml value(s) for 'mode'."),
                                        Optional('config-json'):
                                            {
                                                'PublicIps':
                                                    And(list, error="Invalid environment.yml value(s) for 'PublicIps'."),
                                                Optional('Clusters'):
                                                    And(list, error="Invalid environment.yml value(s) for 'Clusters'."),
                                                Optional('InstanceDnsServers'):
                                                    And(list, error="Invalid environment.yml value(s) for 'InstanceDnsServers'."),
                                                Optional('Mode'):
                                                    And(str, error="Invalid environment.yml value(s) for 'Mode'."),
                                            },
                                        'bridge-interface':
                                            And(str, error="Invalid environment.yml value(s) for 'bridge-interface'."),
                                        Optional('bridged-nic'):
                                            And(str, error="Invalid environment.yml value(s) for 'bridge-nic'."),
                                        Optional('public-interface'):
                                            And(str, error="Invalid environment.yml value(s) for 'public-interface'."),
                                        Optional('private-interface'):
                                            And(str, error="Invalid environment.yml value(s) for 'private-interface'."),
                                        Optional('nc-router'):
                                            And(str, error="Invalid environment.yml value(s) for 'nc-router'."),
                                    },
                                'topology':
                                    {
                                        'clusters': And(dict, error="Invalid environment.yml value(s) for 'clusters'."),
                                        'clc-1': And(str, error="Invalid environment.yml value(s) for 'clc-1'."),
                                        'walrus': And(str, error="Invalid environment.yml value(s) for 'walrus'."),
                                        'user-facing':
                                            And(list, error="Invalid environment.yml value(s) for 'user-facing'."),
                                        Optional('riakcs'): {
                                            'access-key':
                                                And(str, error="Invalid environment.yml value(s) for 'access-key'."),
                                            'admin-email':
                                                And(str, error="Invalid environment.yml value(s) for 'access-email'."),
                                            'admin-name':
                                                And(str, error="Invalid environment.yml value(s) for 'access-name'."),
                                            'endpoint':
                                                And(str, error="Invalid environment.yml value(s) for 'endpoint'."),
                                            'port':
                                                And(int, error="Invalid environment.yml value(s) for 'port'."),
                                            'secret-key':
                                                And(str, error="Invalid environment.yml value(s) for 'secret-key'."),
                                        }
                                    },
                                'eucalyptus-repo':
                                    And(str, error="Invalid environment.yml value(s) for 'eucalyptus-repo'."),
                                'euca2ools-repo':
                                    And(str, error="Invalid environment.yml value(s) for 'euca2ools-repo'."),
                                Optional('default-img-url'):
                                    And(str, error="Invalid environment.yml value(s) for 'default-img-url'."),
                                Optional('enterprise-repo'):
                                    And(str, error="Invalid environment.yml value(s) for 'enterprise-repo'."),
                                Optional('init-script-url'):
                                    And(str, error="Invalid environment.yml value(s) for 'init-script-url'."),
                                Optional('post-script-url'):
                                    And(str, error="Invalid environment.yml value(s) for 'post-script-url'."),
                                Optional('yum-options'):
                                    And(str, error="Invalid environment.yml value(s) for 'yum-options'."),
                                Optional('nc'):
                                    And(dict, error="Invalid environment.yml value(s)(s) for 'nc'."),
                                Optional('install-imaging-worker'):
                                    And(str, error="Invalid environment.yml value(s) for 'install-imaging-worker'."),
                                Optional('install-load-balancer'):
                                    And(str, error="Invalid environment.yml value(s) for 'install-load-balancer'."),
                                Optional('install-type'):
                                    And(str, error="Invalid environment.yml value(s) for 'install-type'."),
                                Optional('log-level'):
                                    And(str, error="Invalid environment.yml value(s) for 'log-level'."),
                                Optional('source-branch'):
                                    And(str, error="Invalid environment.yml value(s) for 'source-branch'."),
                                Optional('source-repo'):
                                    And(str, error="Invalid environment.yml value(s) for 'source-repo'."),
                                Optional('system-properties'):
                                    And(dict, error="Invalid environment.yml value(s) for 'system-properties'.")
                            }
                    }
            }
        )
        self.validated = self.schema.validate(self.envdata)
        try:
            assert self.validated
            self.success("environment.yml file appears to be valid.")
        except AssertionError, e:
            self.failure("environment.yml is invalid!: " + str(e))

