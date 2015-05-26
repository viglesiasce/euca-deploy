from calyptos.plugins.validator.validatorplugin import ValidatorPlugin
from urllib2 import Request, urlopen, URLError


class Repos(ValidatorPlugin):
    def validate(self):
        eucalyptus_attributes = self.environment['default_attributes']['eucalyptus']
        self.repotypes = ['enterprise-repo', 'default-img-url', 'euca2ools-repo', 'eucalyptus-repo', 'init-script-url', 'post-script-url']
        self.repos = []
        for val in self.repotypes:
            if val in eucalyptus_attributes:
                self.repos.append(eucalyptus_attributes[val])
        for url in self.repos:
            req = Request(url)
            try:
                response = urlopen(req)
                self.success('URL: ' + str(url) + ' is valid and reachable!')
            except URLError, e:
                if hasattr(e, 'reason'):
                    raise AssertionError("INVALID URL: " + str(url) + "  " + str(e.reason))
                elif hasattr(e, 'code'):
                    raise AssertionError("INVALID REQUEST: " + str(url) + "  " + str(e.code))
