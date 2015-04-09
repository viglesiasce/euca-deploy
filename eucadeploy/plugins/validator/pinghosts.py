from eucadeploy.plugins.validator.validatorplugin import ValidatorPlugin
import os

class PingHosts(ValidatorPlugin):
    def validate(self):
        failed = 0
        passed = 0
        for host in self.component_deployer.all_hosts:
            if self._ping(host, count=3):
                self.success('Ping to ' + host)
                passed += 1
            else:
                self.failure('Ping to ' + host)
                failed += 1
        self.report(failed, passed)

    def _ping(self, host, count=1):
        exit_code = os.system('ping -c {0} {1}'.format(count, host))
        if exit_code != 0:
            return False
        else:
            return True
