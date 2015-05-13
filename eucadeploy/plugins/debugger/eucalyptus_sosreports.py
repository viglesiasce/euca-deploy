from fabric.context_managers import hide
import re
from eucadeploy.plugins.debugger.debuggerplugin import DebuggerPlugin



class EucalyptusSosReports(DebuggerPlugin):
    def debug(self):
        all_hosts = self.component_deployer.all_hosts
        roles = self.component_deployer.get_roles()
        """
        Check to make sure sos and eucalyptus-sos-plugins
        packages are installed
        """
        packages = ['sos', 'eucalyptus-sos-plugins']
        self._check_packages(all_hosts, packages)
        """
        Run sosreports on all components; 
        download sosreports to local client
        """
        self._grab_sosreports(all_hosts)

        return (self.passed, self.failed)

    def _check_packages(self, all_hosts, packages):
        for package in packages:
            with hide('everything'):
                """
                Use rpm --query --all to confirm package
                exists; if not, issue a warning and install
                missing package
                """
                rpm_output = self.run_command_on_hosts('rpm ' 
                             + '--query --all ' + package,
                             hosts=all_hosts)
            for host in all_hosts:
                if re.search(package, rpm_output[host]):
                    self.success(host + ':Package found - ' + package)
                else:
                    self.warning(host + ':Package not installed - '
                                + package + '; Installing ' + package)
                    with hide('everything'):
                        yum_output = self.run_command_on_host('yum install '
                                     + ' --assumeyes --quiet --nogpgcheck ' + package,
                                     host=host)
                    if not yum_output:
                        self.success(host + ':Package installed - ' + package)
                    else:
                        self.failure(host + ':Package failed to install - ' + package)

    def _grab_sosreports(self, all_hosts):
        """
        Remove old sosreports are around in /tmp
        """
        with hide('everything'):
            rm_output = self.run_command_on_hosts('rm -rf /tmp/sosreport*',
                                                  hosts=all_hosts)
        for host in all_hosts:
            if not rm_output[host]:
                self.success(host + ':old sosreports successfully removed')
            else:
                self.failure(host + ':old sosreports failed to be removed')

        with hide('everything'):
            """
            Execute sosreport on all hosts
            """
            sosreport_output = self.execute_sosreports_on_hosts('sosreport ',
                                                                hosts=all_hosts)
        for host in all_hosts:
            """
            Confirm sosreport ran successfully;
            Download sosreport to local client
            """
            hostname = host.replace(".", '')
            for output in sosreport_output[host].split('\n'):
                sosfile = 'sosreport-' + hostname
                sosreport_file = re.search(sosfile, output, re.I)
                if sosreport_file:
                    self.success(host + ':sosreport finished - '
                                + output)
                    remote_path = output.strip()
                    local_path = remote_path.split('/')[2]
                    format_host = host.replace(".", "_")
                    with hide('everything'):
                        cp_output = self.get_command_on_host(remote_path,
                                                             format_host
                                                             + "-"
                                                             + local_path,
                                                             host=host)
                    if cp_output:
                        self.success(host + ':sosreport downloaded - '
                                    + local_path)
                    else:
                        self.failure(host + ':sosreport failed to download - '
                                    + local_path)
