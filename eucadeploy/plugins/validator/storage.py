from eucadeploy.plugins.validator.validatorplugin import ValidatorPlugin

class Storage(ValidatorPlugin):
    def validate(self):
        self.topology = self.environment['default_attributes']['eucalyptus']['topology']
        self.enveuca = self.environment['default_attributes']['eucalyptus']
        if 'system-properties' in self.enveuca:
            self.systemproperties = self.environment['default_attributes']['eucalyptus']['system-properties']
        for name in self.topology['clusters'].keys():
            if 'storage-backend' in self.topology['clusters'][name]:
                if 'netapp' in self.topology['clusters'][name]['storage-backend']:
                    assert self.systemproperties[name + '.storage.chapuser']
                    self.success('Netapp system property ' + name + '.storage.chapuser is valid.')
                    assert self.systemproperties[name + '.storage.ncpaths']
                    self.success('Netapp system property ' + name + '.storage.ncpaths is valid.')
                    assert self.systemproperties[name + '.storage.scpaths']
                    self.success('Netapp system property ' + name + '.storage.scpaths is valid.')
                    assert self.systemproperties[name + '.storage.sanhost']
                    self.success('Netapp system property ' + name + '.storage.sanhost is valid.')
                    assert self.systemproperties[name + '.storage.sanpassword']
                    self.success('Netapp system property ' + name + '.storage.sanpassword is valid.')
                    assert self.systemproperties[name + '.storage.sanuser']
                    self.success('Netapp system property ' + name + '.storage.sanuser is valid.')
                    assert self.systemproperties[name + '.storage.vservername']
                    self.success('Netapp system property ' + name + '.storage.vservername is valid.')
