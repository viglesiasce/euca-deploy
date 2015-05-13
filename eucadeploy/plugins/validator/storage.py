from eucadeploy.plugins.validator.validatorplugin import ValidatorPlugin

class Storage(ValidatorPlugin):
    def validate(self):
        self.topology = self.environment['default_attributes']['eucalyptus']['topology']
        self.systemproperties = self.environment['default_attributes']['eucalyptus']['system-properties']
        for name in self.topology['clusters'].keys():
            if 'storage-backend' in self.topology['clusters'][name]:
                if 'netapp' in self.topology['clusters'][name]['storage-backend']:
                    assert self.systemproperties[name + '.storage.scpaths']
                    self.success('Netapp system property ' + name + '.storage.scpaths is valid.')
                    #raise AssertionError("Netapp system property  " + name + " NOT FOUND")

