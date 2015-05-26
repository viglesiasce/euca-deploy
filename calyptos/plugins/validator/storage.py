from calyptos.plugins.validator.validatorplugin import ValidatorPlugin

class Storage(ValidatorPlugin):
    def validate(self):
        self.topology = self.environment['default_attributes']['eucalyptus']['topology']
        if 'system-properties' in self.environment['default_attributes']['eucalyptus']:
            self.systemproperties = self.environment['default_attributes']['eucalyptus']['system-properties']
        for name in self.topology['clusters'].keys():
            if 'storage-backend' in self.topology['clusters'][name]:
                storage_options = ['netapp', 'ceph-rbd', 'threepar']
                netapp_properties = [name + '.storage.chapuser', name + '.storage.ncpaths', name + '.storage.scpaths',
                                     name + '.storage.sanhost', name + '.storage.sanpassword', name +
                                     '.storage.sanuser', name + '.storage.vservername']
                ceph_properties = [name + '.storage.cephconfigfile', name + '.storage.cephkeyringfile',
                                   name + '.storage.cephsnapshotpools', name + '.storage.cephuser',
                                   name + '.storage.cephvolumepools']
                threepar_properties = [name + '.storage.chapuser', name + '.storage.ncpaths', name + '.storage.sanhost',
                                       name + '.storage.sanuser', name + '.storage.sanpassword', name +
                                       '.storage.scpaths', name + '.storage.threeparwsport', name + '.storage.usercpg',
                                       name + '.storage.copycpg']
                for val1 in storage_options:
                    if val1 in self.topology['clusters'][name]['storage-backend']:
                        if val1 == "netapp":
                            storage_properties = netapp_properties
                        if val1 == "ceph-rbd":
                            storage_properties = ceph_properties
                        if val1 == "threepar":
                            storage_properties = threepar_properties
                        for val2 in storage_properties:
                           try:
                              assert val2 in self.systemproperties
                              self.success(val1 + ' system property ' + val2 + ' is present.')
                           except AssertionError, e:
                              self.failure(val1 + ' system property ' + val2 + ' is missing or invalid!  ' + str(e))
