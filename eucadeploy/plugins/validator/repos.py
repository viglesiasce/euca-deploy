from eucadeploy.plugins.validator.validatorplugin import ValidatorPlugin
import urllib2


class Repos(ValidatorPlugin):
    def validate(self):
        self.repos = [self.environment['default_attributes']['eucalyptus']['enterprise-repo']]
        self.repos += [self.environment['default_attributes']['eucalyptus']['init-script-url']]
#        print self.repos
        for url in self.repos:
            print "URL: " + str(url)
            from urllib2 import Request, urlopen, URLError
            req = Request(url)
            try:
                response = urlopen(req)
            except URLError, e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
                return False
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
                return False
            else:
                # everything is fine
                print "Success!"
                return True


#    def _ping(self, host, count=1):
#        exit_code = os.system('ping -c {0} {1}'.format(count, host))
#        if exit_code != 0:
#            return False
#        else:
#            return True
