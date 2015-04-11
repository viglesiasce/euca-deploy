from fabric.context_managers import hide
import re
from eucadeploy.plugins.debugger.debuggerplugin import DebuggerPlugin

class DebugCloudController(DebuggerPlugin):
    def debug(self):
        clcs = self.component_deployer.roles['clc']
        ### Collect information
        with hide('everything'):
            clc_service_state = self.run_command_on_hosts('service eucalyptus-cloud status', hosts=clcs)
            describe_services = self.run_command_on_hosts('euca-describe-services', hosts=clcs)
        for clc in clcs:
            if re.search('running', clc_service_state[clc]):
                self.success(clc + ': CLC service running')
            else:
                self.failure(clc + ': CLC service not running')
            for state in ['DISABLED', 'BROKEN', 'NOTREADY']:
                search = re.search('.*' + state + '.*', describe_services[clc])
                if search:
                    self.failure(clc + ': Some services are in ' + state)
                    print search.group()
                else:
                    self.success(clc + ': No services in ' + state)