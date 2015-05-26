from fabric.context_managers import hide, show
import re
from calyptos.plugins.debugger.debuggerplugin import DebuggerPlugin


class FilePermissions(DebuggerPlugin):
    def debug(self):
        all_hosts = self.component_deployer.all_hosts
        roles = self.component_deployer.get_roles()
        common_files = {'eucalyptus': ['/var/lib/eucalyptus',
                                    '/var/log/eucalyptus'],
                        'root': []}

        for host in all_hosts:
            self._check_file_owner(host, common_files)
            if host in roles['clc']:
                pass
            if host in roles['node-controller']:
                pass



        return (self.passed, self.failed)

    def _check_file_owner(self, host, path_dict):
        for owner, paths in path_dict.iteritems():
            for path in paths:
                with hide('everything'):
                    stat_output = self.run_command_on_host('stat -c %U ' + path, host=host)
                if re.search(owner, stat_output):
                    self.success(host + ': File permisssions correct for ' + path)
                else:
                    self.failure(host + ': File permisssions incorrect for ' + path)
