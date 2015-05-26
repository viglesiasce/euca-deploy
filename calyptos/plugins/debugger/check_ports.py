from fabric.context_managers import hide
import re
from calyptos.plugins.debugger.debuggerplugin import DebuggerPlugin

class CheckPorts(DebuggerPlugin):
    def debug(self):
        all_hosts = self.component_deployer.all_hosts
        with hide('everything'):
            ports = self.run_command_on_hosts('netstat -lnp', all_hosts)
        roles = self.component_deployer.get_roles()
        clc_ports = {'tcp': [8773, 8777, 53, 8443, 8779],
                     'udp': [53, 7500, 18778]}
        cc_ports = {'tcp': [8774],
                    'udp': []}
        sc_ports = {'tcp': [8773],
                    'udp': []}
        nc_ports = {'tcp': [8775],
                    'udp': []}
        def check_port_map(port_map):
            for proto, ports in port_map.iteritems():
                for port in ports:
                    if not self._check_port(netstat, proto, port, host):
                        closed_ports.append(port)
        for host, netstat in ports.iteritems():
            closed_ports = []
            if host in roles['clc']:
                check_port_map(clc_ports)
            if host in roles['cluster-controller']:
                check_port_map(cc_ports)
            if host in roles['storage-controller']:
                check_port_map(sc_ports)
            if host in roles['node-controller']:
                check_port_map(nc_ports)
            if closed_ports:
                raise AssertionError('Required ports '
                                     'not open on host ' + host + '\n' +
                                     str(closed_ports))
        return (self.passed, self.failed)

    def _check_port(self, netstat, proto, port, host):
        port_string = proto + '.*:' + str(port)
        search = re.search(port_string, netstat)
        if search:
            self.success(host + ': Open ' + port_string)
            return True
        else:
            self.failure(host + ': Closed ' + port_string)
            return False

