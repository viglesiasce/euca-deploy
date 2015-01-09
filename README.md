# Euca Deploy

This is a harness for running the Eucalyptus cookbook against a distributed system of nodes without a dependency on a Chef Server. We are using fabric and chef-zero to emulate the functionality of a chef-server. 

## Install

### On a CentOS 6 system:

    yum install -y python-devel gcc
    easy_install fabric PyYAML
    yum install -y https://opscode-omnibus-packages.s3.amazonaws.com/el/6/x86_64/chefdk-0.3.5-1.x86_64.rpm
    git clone https://github.com/viglesiasce/euca-deploy
    pushd euca-deploy
    chef generate chef-repo
    mkdir -p chef-repo/environments
    mkdir -p chef-repo/nodes
    git clone https://github.com/eucalyptus/eucalyptus-cookbook
    berks vendor --berksfile eucalyptus-cookbook/Berksfile chef-repo/cookbooks
    
## Deploy

- Edit the config.yml file to match your deployment topology and configuration
- Run ```fab install```
    
    
    
    
    
