# stevedore/example/base.py
import abc
import fabric
from fabric.colors import red, green, cyan, yellow, white
from fabric.decorators import task
from fabric.operations import run, get, settings
from fabric.state import env
from fabric.tasks import execute
import six


@six.add_metaclass(abc.ABCMeta)
class DebuggerPlugin(object):
    #Base class for example plugin used in the tutorial.

    def __init__(self, component_deployer):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.message_style = "[{0: <20}] {1}"
        self.name = self.__class__.__name__
        self.component_deployer = component_deployer
        self.environment = self.component_deployer.read_environment()
        self.roles = self.component_deployer.get_roles()
        print cyan(self.message_style.format('DEBUG STARTING', self.name))

    def __del__(self):
        self.report()

    def success(self, message):
        # Function to display and tally success of a debug step
        self.passed +=1
        print green(self.message_style.format('DEBUG PASSED', message))

    def failure(self, message):
        # Function to display and tally a failure of a debug step
        self.failed +=1
        print red(self.message_style.format('DEBUG FAILED', message))

    def info(self, message):
        # Function to display information of a debug step
        print white(self.message_style.format('INFO', message))

    def warning(self, message):
        # Function to display and tally a warning of a debug step
        self.warnings +=1
        print yellow(self.message_style.format('DEBUG WARNING', message))

    def report(self):
        # Function to display report of debug results
        text_color = red
        if self.failed == 0:
            text_color = cyan
        print text_color(self.message_style.format('DEBUG RESULTS',
                                             "Name: {0} Passed: "
                                             "{1} Failed: {2}".format(
                                              self.name,
                                              str(self.passed),
                                              str(self.failed))))

    @task
    def run_command_task(command, user='root', password='foobar'):
        # Task to run command on host and return result
        env.user = user
        env.password = password
        env.parallel = True
        return run(command)

    @task
    def get_file_task(remote_path, local_path, user='root', password='foobar'):
        # Task to grab file from host and return result
        env.user = user
        env.password = password
        env.parallel = True
        with settings(warn_only=True):
            return get(remote_path, local_path)

    def get_file_on_host(self, remote_path, local_path, host):
        # Function to execute get_file_task on host
        return execute(self.get_file_task, remote_path=remote_path,
                       local_path=local_path, host=host)[host]

    def run_command_on_hosts(self, command, hosts, host=None):
        # Function to execute run_command_task on list of hosts
        return execute(self.run_command_task, command=command, hosts=hosts)

    def run_command_on_host(self, command, host):
        # Function to execute run_command_task on host
        return execute(self.run_command_task, command=command, host=host)[host]

    def debug(self):
        """Format the data and return unicode text.

        :param data: A dictionary with string keys and simple types as
                     values.
        :type data: dict(str:?)
        :returns: Iterable producing the formatted text.
        """
