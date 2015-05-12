from eucadeploy.plugins.validator.validatorplugin import ValidatorPlugin
from urllib2 import Request, urlopen, URLError


class Repos(ValidatorPlugin):
    def validate(self):
        eucalyptus_attributes = self.environment['default_attributes']['eucalyptus']
        self.repos = []
        if 'enterprise-repo' in eucalyptus_attributes:
            self.repos.append(eucalyptus_attributes['enterprise-repo'])
        if 'default-img-url' in eucalyptus_attributes:
            self.repos.append(eucalyptus_attributes['default-img-url'])
        if 'euca2ools-repo' in eucalyptus_attributes:
            self.repos.append(eucalyptus_attributes['euca2ools-repo'])
        if 'eucalyptus-repo' in eucalyptus_attributes:
            self.repos.append(eucalyptus_attributes['eucalyptus-repo'])
        if 'init-script-url' in eucalyptus_attributes:
            self.repos.append(eucalyptus_attributes['init-script-url'])
        if 'post-script-url' in eucalyptus_attributes:
            self.repos.append(eucalyptus_attributes['post-script-url'])
        for url in self.repos:
            req = Request(url)
            try:
                response = urlopen(req)
                self.success('URL: ' + str(url) + ' is valid and reachable!')
            except URLError, e:
                if hasattr(e, 'reason'):
                    raise AssertionError("INVALID URL: " + str(url) + "  " + str(e.reason))
                elif hasattr(e, 'code'):
                    raise AssertionError("INVALID REQUEST: " + str(url) + "  " + str(e.reason))
