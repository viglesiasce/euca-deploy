from eucadeploy.plugins.validator.validatorplugin import ValidatorPlugin

class Storage(ValidatorPlugin):
    def validate(self):
        self.topology = self.environment['default_attributes']['eucalyptus']['topology']
        if 'system-properties' in self.environment['default_attributes']['eucalyptus']:
            self.systemproperties = self.environment['default_attributes']['eucalyptus']['system-properties']
        for name in self.topology['clusters'].keys():
            if 'storage-backend' in self.topology['clusters'][name]:
                if 'netapp' in self.topology['clusters'][name]['storage-backend']:
                    storage_properties = [name + '.storage.chapuser', name + '.storage.ncpaths', name + '.storage.scpaths',
                                    name + '.storage.sanhost', name + '.storage.sanpassword', name + '.storage.sanuser',
                                    name + '.storage.vservername']
                    for val in storage_properties:
                        try:
                           assert val in self.systemproperties
                           self.success('Netapp system property ' + val + ' is valid.')
                        except AssertionError, e:
                           self.failure('Netapp system property ' + val + ' is missing or invalid')
                if 'ceph-rbd' in self.topology['clusters'][name]['storage-backend']:
                    storage_properties = [name + '.storage.cephconfigfile', name + '.storage.cephkeyringfile',
                                    name + '.storage.cephsnapshotpools', name + '.storage.cephuser',
                                    name + '.storage.cephvolumepools']
                    for val in storage_properties:
                        try:
                           assert val in self.systemproperties
                           self.success('Netapp system property ' + val + ' is valid.')
                        except AssertionError, e:
                           self.failure('Netapp system property ' + val + ' is missing or invalid')
                if 'threepar' in self.topology['clusters'][name]['storage-backend']:
                    storage_properties = [name + '.storage.chapuser', name + '.storage.ncpaths', name + '.storage.sanhost',
                                    name + '.storage.sanuser', name + '.storage.sanpassword', name + '.storage.scpaths',
                                    name + '.storage.threeparwsport', name + '.storage.usercpg', name + '.storage.copycpg']
                    for val in storage_properties:
                        try:
                           assert val in self.systemproperties
                           self.success('Netapp system property ' + val + ' is valid.')
                        except AssertionError, e:
                           self.failure('Netapp system property ' + val + ' is missing or invalid')
