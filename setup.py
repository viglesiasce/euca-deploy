#!/usr/bin/env python

from distutils.command.build_py import build_py
from distutils.command.sdist import sdist
import os.path
import subprocess
import glob

from setuptools import setup, find_packages


__version__ = '0.1'


# Check if this is a git repo; maybe we can get more precise version info
try:
    REPO_PATH = "."
    # noinspection PyUnresolvedReferences
    GIT = subprocess.Popen(
        # TODO: mbacchi change this to "git describe --tag" when first git tag has been defined 
        ['git', 'describe', '--always'], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={'GIT_DIR': os.path.join(REPO_PATH, '.git')})
    GIT.wait()
    GIT.stderr.read()
    if GIT.returncode == 0:
        __version__ = GIT.stdout.read().strip().lstrip('v')
        if type(__version__).__name__ == 'bytes':
            __version__ = __version__.decode()
except:
    # Not really a bad thing; we'll just use what we had
    pass

class build_py_with_git_version(build_py):
    '''Like build_py, but also hardcoding the version in __init__.__version__
       so it's consistent even outside of the source tree'''

    def build_module(self, module, module_file, package):
        orig_outfile, _ = build_py.build_module(self, module, module_file,
                                                package)
        version_line = "__version__ = '{0}'\n".format(__version__)
        new_outfile = orig_outfile + '.new'
        with open(new_outfile, 'w') as new_fh:
            with open(orig_outfile) as orig_fh:
                for line in orig_fh:
                    if line.startswith('__version__ ='):
                        new_fh.write(version_line)
                    else:
                        new_fh.write(line)
            new_fh.flush()
        os.rename(new_outfile, orig_outfile)


class sdist_with_git_version(sdist):
    '''Like sdist, but also hardcoding the version in __init__.__version__ so
       it's consistent even outside of the source tree'''

    def make_release_tree(self, base_dir, files):
        sdist.make_release_tree(self, base_dir, files)
        version_line = "__version__ = '{0}'\n".format(__version__)
        orig_setup = os.path.join(base_dir, 'setup.py')
        new_setup = orig_setup + '.new'
        with open(new_setup, 'w') as new_fh:
            with open(orig_setup) as orig_fh:
                for line in orig_fh:
                    if line.startswith('__version__ ='):
                        new_fh.write(version_line)
                    else:
                        new_fh.write(line)
            new_fh.flush()
        os.rename(new_setup, orig_setup)


with open('README.md') as f:
    long_description = f.read()

example_items = glob.glob('examples/*')

setup(
    name='calyptos',
    version=__version__,
    description='Tool for installing Eucalyptus',
    long_description=long_description,
    author='Vic Iglesias',
    author_email='viglesiasce@gmail.com',
    url='https://github.com/eucalyptus/calyptos/',
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=['fabric', 'PyYaml', 'argparse', 'stevedore', 'sphinx'],
    scripts=['bin/calyptos'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Clustering',
        'Topic :: System :: Systems Administration',
    ],
    entry_points={
        'calyptos.deployer': [
            'chef = calyptos.plugins.deployer.'
            'chef:Chef'
        ],
        'calyptos.validator': [
            'pinghosts = calyptos.plugins.validator.'
            'pinghosts:PingHosts',
            'topology = calyptos.plugins.validator.'
            'topology:Topology',
            'repos = calyptos.plugins.validator.'
            'repos:Repos',
            'storage = calyptos.plugins.validator.'
            'storage:Storage',
            'structure = calyptos.plugins.validator.'
            'structure:Structure'
        ],
        'calyptos.debugger': [
            'check_ports = calyptos.plugins.debugger.'
            'check_ports:CheckPorts',
            'debug_cloud_controller = calyptos.plugins.debugger.'
            'debug_cloud_controller:DebugCloudController',
            'debug_node_controller = calyptos.plugins.debugger.'
            'debug_node_controller:DebugNodeController',
            'debug_cluster_controller = calyptos.plugins.debugger.'
            'debug_cluster_controller:DebugClusterController',
            'file_permissions = calyptos.plugins.debugger.'
            'file_permissions:FilePermissions',
            'eucalyptus_sosreports = calyptos.plugins.debugger.'
            'eucalyptus_sosreports:EucalyptusSosReports'
        ]
    },
    cmdclass={
        'build_py': build_py_with_git_version,
        'sdist': sdist_with_git_version
    },
    data_files=[('/etc/calyptos/', ['etc/config.yml']),
	('/usr/share/calyptos/examples/', example_items)],
)
