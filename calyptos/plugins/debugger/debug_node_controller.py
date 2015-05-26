from fabric.context_managers import hide
import re
from calyptos.plugins.debugger.debuggerplugin import DebuggerPlugin

class DebugNodeController(DebuggerPlugin):
    def debug(self):
        nodes = self.component_deployer.roles['node-controller']
        ### Collect information
        with hide('everything'):
            nc_service_state = self.run_command_on_hosts('service eucalyptus-nc status', hosts=nodes)
            libvirt_service_state = self.run_command_on_hosts('service libvirtd status', hosts=nodes)

        for node in nodes:
            if re.search('running', nc_service_state[node]):
                self.success(node + ': NC service running')
            else:
                self.failure(node + ': NC service not running')
            if re.search('running', libvirt_service_state[node]):
                self.success(node + ': libvirt service running')
            else:
                self.failure(node + ': libvirt service not running')
        return (self.passed, self.failed)