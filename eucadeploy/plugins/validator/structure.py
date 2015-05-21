from eucadeploy.plugins.validator.validatorplugin import ValidatorPlugin
from schema import Schema, And, Or, Use, Optional
import yaml

class Structure(ValidatorPlugin):
    def validate(self):
        self.envdata = self.environment
        self.schema = Schema({'description': str,
                              'name': str,
                              Optional('cookbook_versions'): dict,
                              Optional('override_attributes'): dict,
                              'default_attributes': {'eucalyptus': {'network': {'mode': str,
                                                                   'config-json': {
                                                                       'PublicIps': list,
                                                                       Optional('Clusters'): list,
                                                                       Optional('InstanceDnsServers'): list},
                                                                   'bridge-interface': str,
                                                                   Optional('bridged-nic'): str,
                                                                   Optional('public-interface'): str,
                                                                   Optional('private-interface'): str,
                                                                   Optional('nc-router'): str,
                                                                   },
                                                                    'topology': {'clusters': dict,
                                                                                 'clc-1': str,
                                                                                 'walrus': str,
                                                                                 'user-facing': list
                                                                                 },
                                                                    'eucalyptus-repo': str,
                                                                    'euca2ools-repo': str,
                                                                    Optional('default-img-url'): str,
                                                                    Optional('enterprise-repo'): str,
                                                                    Optional('init-script-url'): str,
                                                                    Optional('post-script-url'): str,
                                                                    Optional('yum-options'): str,
                                                                    Optional('nc'): dict,
                                                                    Optional('install-imaging-worker'): str,
                                                                    Optional('install-load-balancer'): str,
                                                                    Optional('install-type'): str,
                                                                    Optional('log-level'): str,
                                                                    Optional('source-branch'): str,
                                                                    Optional('source-repo'): str,
                                                                    Optional('system-properties'): dict
                                                                    }
                                                     }
                              }
                             )
        self.validated = self.schema.validate(self.envdata)
        try:
            assert self.validated
            self.success("environment.yml file appears to be valid!")
        except AssertionError, e:
            self.failure("environment.yml is invalid!: " + str(e))
