#!/usr/bin/env python

from __future__ import with_statement

from setuptools import setup, find_packages

from eucadeploy.version import get_version


with open('README.md') as f:
    long_description = f.read()

setup(
    name='Euca Deploy',
    version=get_version(),
    description='Tool for installing Eucalyptus',
    long_description=long_description,
    author='Vic Iglesias',
    author_email='viglesiasce@gmail.com',
    url='https://github.com/viglesiasce/euca-deploy/',
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=['fabric', 'PyYaml', 'argparse'],
    scripts=['bin/euca-deploy'],
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
)
