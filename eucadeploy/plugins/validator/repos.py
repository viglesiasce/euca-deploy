from eucadeploy.plugins.validator.validatorplugin import ValidatorPlugin
from urllib2 import Request, urlopen, URLError


class Repos(ValidatorPlugin):
    def validate(self):
        self.repos = [self.environment['default_attributes']['eucalyptus']['enterprise-repo']]
        self.repos += [self.environment['default_attributes']['eucalyptus']['default-img-url']]
        self.repos += [self.environment['default_attributes']['eucalyptus']['euca2ools-repo']]
        self.repos += [self.environment['default_attributes']['eucalyptus']['eucalyptus-repo']]
        self.repos += [self.environment['default_attributes']['eucalyptus']['init-script-url']]
        for url in self.repos:
            req = Request(url)
            try:
                response = urlopen(req)
            except URLError, e:
                if hasattr(e, 'reason'):
                    raise AssertionError("INVALID URL: " + str(url) + "  " + str(e.reason))
                elif hasattr(e, 'code'):
                    raise AssertionError("INVALID REQUEST: " + url + "  " + str(e.reason))
            else:
                # everything is fine
                self.success('URL: ' + url + ' is valid and reachable!')
