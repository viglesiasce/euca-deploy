from fabric.context_managers import hide
import re
from calyptos.plugins.debugger.debuggerplugin import DebuggerPlugin

class DebugClusterController(DebuggerPlugin):
    def debug(self):
        ccs = self.component_deployer.roles['cluster-controller']
        ### Collect information
        with hide('everything'):
            cc_service_state = self.run_command_on_hosts('service eucalyptus-cc status', hosts=ccs)

        for cc in ccs:
            if re.search('running', cc_service_state[cc]):
                self.success(cc + ': CC service running')
            else:
                self.failure(cc + ': CC service not running')
        return (self.passed, self.failed)
