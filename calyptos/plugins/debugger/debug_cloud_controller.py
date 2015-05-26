from fabric.context_managers import hide, show
import re
from calyptos.plugins.debugger.debuggerplugin import DebuggerPlugin


class DebugCloudController(DebuggerPlugin):
    def debug(self):
        clcs = self.component_deployer.roles['clc']
        with hide('everything'):
            for clc in clcs:
                self._check_service_running(clc)
                self._services_enabled(clc)
                self._psql_available(clc)
                self._db_size_check(clc)
                self._var_lib_euca_size_check(clc)
                self._memory_usage(clc)
                # If you  are debugging checks they can go here
                # for more verbose output
                with show('everything'):
                    pass
        return (self.passed, self.failed)

    def _check_service_running(self, clc):
        clc_service_state = self.run_command_on_host(
            'service eucalyptus-cloud status', host=clc)
        if re.search('running', clc_service_state):
            self.success(clc + ': CLC service running')
        else:
            self.failure(clc + ': CLC service not running')

    def _services_enabled(self, clc):
        describe_services = self.run_command_on_host('euca-describe-services',
                                                     host=clc)
        for state in ['DISABLED', 'BROKEN', 'NOTREADY']:
            search = re.search('.*' + state + '.*', describe_services)
            if search:
                self.failure(clc + ': Some services are in ' + state)
                print search.group()
            else:
                self.success(clc + ': No services in ' + state)

    def _psql_available(self, clc):
        psql_dt = 'echo "\pset pager false;\dt *.*;" | psql -h /var/lib/eucalyptus/db/data/ -p 8777 eucalyptus_shared'
        psql_dt_out = self.run_command_on_host(psql_dt, host=clc)
        if re.search('eucalyptus_cloud', psql_dt_out):
            self.success(clc + ': Was able to access postgres DB')
        else:
            self.failure(clc + ': Unable to connect to postgres DB  ')
            print psql_dt_out

    def _db_size_check(self, clc):
        db_size = 'du -s /var/lib/eucalyptus/db/'
        db_size_out = self.run_command_on_host(db_size, host=clc)
        db_size_mb = int(db_size_out.split()[0]) / 1024
        if db_size_mb > 3000:
            self.failure(clc + ': Database is larger than 3GB. '
                               'Consider removing reporting '
                               'data with eureport-delete-data')
        else:
            self.success(clc + ': DB size smaller than 3GB  ')

    def _var_lib_euca_size_check(self, clc):
        df_vle = 'df -h --sync /var/lib/eucalyptus/ -P | ' \
                 'awk \'{print $5}\' | grep -v Use'
        vle_size = self.run_command_on_host(df_vle, host=clc)
        vle_usage = int(vle_size.strip('%'))
        if vle_usage > 85:
            self.failure(clc + ': /var/lib/eucalyptus is more that 85% full. '
                               'Consider deleting some files from '
                               'that filesystem')
        else:
            self.success(clc + ': /var/lib/eucalyptus is less than 85% full  ')

    def _memory_usage(self, clc):
        free_mem = 'free | grep buffers | grep -v free | awk \'{print $3}\''
        free_mem_size = int(self.run_command_on_host(free_mem, host=clc))
        if free_mem_size < 2000000:
            self.failure(clc + ': Less than 2GB of memory available. '
                               'Consider stop other process on this host')
        else:
            self.success(clc + ': 2GB+ of memory free  ')