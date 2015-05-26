# stevedore/example/base.py
import abc
from fabric.colors import red, green, cyan
import six


@six.add_metaclass(abc.ABCMeta)
class ValidatorPlugin(object):
    """Base class for example plugin used in the tutorial.
    """

    def __init__(self, component_deployer):
        self.message_style = "[{0: <20}] {1}"
        self.name = self.__class__.__name__
        self.component_deployer = component_deployer
        self.environment = self.component_deployer.read_environment()
        self.roles = self.component_deployer.get_roles()
        print cyan(self.message_style.format('TEST STARTING', self.name))

    def success(self, message):
        print green(self.message_style.format('VALIDATION PASSED', message))

    def failure(self, message):
        print red(self.message_style.format('VALIDATION FAILED', message))

    def report(self, failed, passed):
        print cyan(self.message_style.format('TEST RESULTS',
                                             "Name: {0} Passed: "
                                             "{1} Failed: {2}  ".format(
                                                 self.name,
                                                 str(passed),
                                                 str(failed))))

    def validate(self):
        """Format the data and return unicode text.

        :param data: A dictionary with string keys and simple types as
                     values.
        :type data: dict(str:?)
        :returns: Iterable producing the formatted text.
        """