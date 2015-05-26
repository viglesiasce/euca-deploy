from calyptos.plugins.validator.validatorplugin import ValidatorPlugin
import os

class PingHosts(ValidatorPlugin):
    def validate(self):
        for host in self.component_deployer.all_hosts:
            if self._ping(host, count=3):
                self.success('Ping to ' + host)
            else:
                self.failure('Ping to ' + host)
                raise AssertionError('Unable to ping host: ' + host)

    def _ping(self, host, count=1):
        exit_code = os.system('ping -c {0} {1}'.format(count, host))
        if exit_code != 0:
            return False
        else:
            return True
