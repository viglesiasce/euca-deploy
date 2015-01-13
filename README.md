# Euca Deploy

This is a harness for running the Eucalyptus cookbook against a distributed system of nodes without a dependency on a Chef Server. We are using fabric and chef-zero to emulate the functionality of a chef-server. 

## Install

### On a CentOS 6 system:

    yum install -y python-devel gcc git python-setuptools
    easy_install fabric PyYAML
    yum install -y https://opscode-omnibus-packages.s3.amazonaws.com/el/6/x86_64/chefdk-0.3.5-1.x86_64.rpm
    
## Deploy

- Edit the config.yml file to match your deployment topology and configuration
- Prepare your systems
  ```./bin/deployer/euca-deploy prepare -p <root-ssh-password-for-deployment-systems>```
- Bootstrap the CLC
  ```./bin/deployer/euca-deploy bootstrap -p <root-ssh-password-for-deployment-systems>```
- Provision the rest of the system or update the configuration of an existing system
  ```./bin/deployer/euca-deploy provision -p <root-ssh-password-for-deployment-systems>```
    
    
    
    
    
