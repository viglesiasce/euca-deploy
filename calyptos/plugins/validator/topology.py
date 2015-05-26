from calyptos.plugins.validator.validatorplugin import ValidatorPlugin

class Topology(ValidatorPlugin):
    def validate(self):
        self.failed_hosts = []
        self.good_hosts = []
        # Check each cluster
        self._single_cluster_per_host()

        self.topology = self.environment['default_attributes']['eucalyptus']['topology']
        assert self.roles['clc']
        assert self.roles['walrus']
        assert self.roles['user-facing']
        for name in self.topology['clusters'].keys():
            assert self.topology['clusters'][name]['cc-1']
            assert self.topology['clusters'][name]['sc-1']
            self.success('Cluster ' + name + ' has both an SC and CC')
            assert self.topology['clusters'][name]['nodes']
            self.success('Cluster ' + name + ' has node controllers')



    def _single_cluster_per_host(self):
        cluster_hosts = self.roles['cluster']
        for name, hosts in cluster_hosts.iteritems():
            # Check that each host...
            for host in hosts:
                # Only appears in one cluster
                appearances = []
                for cluster in cluster_hosts.keys():
                    if host in cluster:
                        appearances.append(cluster)
                if len(appearances) > 1:
                    raise AssertionError("Found " + host + " in multiple clusters: " + str(
                            appearances))
                else:
                    self.success(host + " only in 1 cluster")
                    self.good_hosts.append(host)









