from fabric.context_managers import hide
import re
from eucadeploy.plugins.debugger.debuggerplugin import DebuggerPlugin



class EucalyptusSosReports(DebuggerPlugin):
    def debug(self):
        all_hosts = self.component_deployer.all_hosts
        roles = self.component_deployer.get_roles()
        packages = ['sos', 'eucalyptus-sos-plugins']

        for host in all_hosts:
            self._check_packages(host, packages)
            self._grab_sosreports(host)


        return (self.passed, self.failed)

    def _check_packages(self, host, packages):
        for package in packages:
            with hide('everything'):
                rpm_output = self.run_command_on_host('rpm ' 
                             + '--query --all ' + package,
                             host=host)
            if re.search(package, rpm_output):
                self.success(host + ':Package found - ' + package)
            else:
                self.warning(host + ':Package not installed - ' + package)
                with hide('everything'):
                    yum_output = self.run_command_on_host('yum install '
                                 + ' --assumeyes --quiet --nogpgcheck ' + package,
                                 host=host)
                if not yum_output:
                    self.success(host + ':Package installed - ' + package)
                else:
                    self.failure(host + ':Package failed to install - ' + package)

    def _grab_sosreports(self, host):
        with hide('everything'):
            hostname = self.run_command_on_host('hostname | cut -d "." -f 1',
                       host=host) 
            sosreport_output = self.run_command_on_host('sosreport '
                                                       + '--name=' + hostname
                                                       + ' --ticket-number=000 '
                                                       + '--batch', host=host)
        for output in sosreport_output.split('\n'):
            sosreport_file = re.search(hostname, output, re.I)
            if sosreport_file:
                import pdb; pdb.set_trace()
                self.success(host + ':sosreport finished - '
                            + output)
                remote = output.strip()
                local = remote.split('/')[2]
                cp_output = self.run_copy_task(remote, local, host)

