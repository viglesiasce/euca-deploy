%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%define name calyptos
%define version 0.1
%define unmangled_version 0.1
%define unmangled_version 0.1
%define release 1

Summary: Tool for managing Eucalyptus
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{tarball_basedir}.tar.xz
License: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Vic Iglesias <viglesiasce@gmail.com>
Url: https://github.com/eucalyptus/calyptos/

BuildRequires: python2-devel
BuildRequires: python-setuptools

Requires: fabric PyYAML git python-stevedore

%description
# Calyptos

This is a tool for managing your Eucalyptus deployments

## Install

### On a CentOS 6 system:

    yum install -y python-devel gcc git python-setuptools
    easy_install fabric PyYAML
    curl -L https://www.opscode.com/chef/install.sh | sudo bash -s -- -P chefdk
    git clone https://github.com/eucalyptus/calyptos
    cd calyptos
    python setup.py install
    
## Lifecycle Actions
The cloud lifecycle is broken down into many phases:

### Configure
The configuration is written in YAML and uses the Chef environment structure. Examples can be found in the examples directory. For a full list of attributes that can be set look at the [Eucalyptus Cookbook attributes](https://github.com/eucalyptus/eucalyptus-cookbook/blob/testing/attributes/default.rb). Edit the etc/environment.yml file to match your deployment topology and configuration.

### Validate
#### Not yet implemented!!!
In this stage we run validations against the configuration file to ensure that the deployment will succeed as we expect.

### Prepare
This step ensures that Chef is installed on all servers and that we can SSH to all of them. It is nice to know that we are on good footing before we get going with the deployment.

    calyptos prepare -p <root-ssh-password-for-deployment-systems>

### Bootstrap
This step deploys the CLC and initializes the database. Here we are getting a bit deeper and if complete, we can assume that we've are on good footing to continue deploying the rest of the cloud.

    calyptos bootstrap -p <root-ssh-password-for-deployment-systems>
  
### Provision
Provisions the rest of the system or update the configuration of an existing system. If you change anything in your environment.yml, you can use this to push that change out to your cloud.

    calyptos provision -p <root-ssh-password-for-deployment-systems>
    
### Debug
#### Not yet implemented!!!
This step will grab all necessary information from a system in order to provide artifacts for use in debugging a problem.
    
    
    


%prep
%setup -q -n %{tarball_basedir}

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install --skip-build --root=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/usr/bin/calyptos
%{python_sitelib}/eucadeploy/*
%{python_sitelib}/*.egg-info
%config /etc/calyptos/config.yml
/usr/share/calyptos/examples/*
