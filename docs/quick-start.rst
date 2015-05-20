Quick Start
-----------
Installation
++++++++++++
In order to install Calyptos you should run the following commands on a CentOS 6 host:

.. code-block:: console

    # yum install -y python-devel gcc git python-setuptools
    # easy_install fabric PyYAML
    # curl -L https://www.opscode.com/chef/install.sh | sudo bash -s -- -P chefdk
    # git clone https://github.com/viglesiasce/euca-deploy
    # cd euca-deploy
    # python setup.py install

Creating your configuration
+++++++++++++++++++++++++++
In order to install Eucalyptus using Calyptos you will first need to create a configuration file that defines your
deployment. Examples for different types of deployments can be found in the ``examples`` directory of the Calyptos
repository.

For details on the various sections of the config file please read the following document:

- :doc:`configuration`

Validating your configuration
+++++++++++++++++++++++++++++
Once you have a config file that describes the Eucalyptus cloud that you intend on deploying, it is best practice to
run the Calyptos validators to make sure that there are no syntactical or semantic mistakes. The validators are intended
to provide feedback based on known mis-configurations that the tool believes will result in either a sub-optimal
or broken deployment. Any failures in this step will not block the continuation of the deployment.

.. code-block:: console

    # calyptos validate -e my-environment.yml

Preparing your deployment machines
++++++++++++++++++++++++++++++++++
The preparation step ensures that all dependencies for the deployment are available. This can include but is not limited
to:

* Ensuring IP connectivity
* Ensuring SSH access
* Ensuring deployment dependencies are in place (Chef, Ansible, etc)

.. code-block:: console

    # calyptos prepare -e my-environment.yml

Bootstrapping your Eucalyptus Cloud Controller
++++++++++++++++++++++++++++++++++++++++++++++
The bootstrap step is used to provision your Cloud Controller (CLC). After completing this step your CLC will be up
and running and have all of its dependent components registered. When this step has completed successfully we will know
a few more things about our deployment:

* We are able to install Eucalyptus from the package repositories we listed in our environment
* Eucalyptus is able to bring up its database without any issues
* We have generated all the necessary keys in order to provision the rest of our components

.. code-block:: console

    # calyptos bootstrap -e my-environment.yml

Provisioning the remaining Eucalyptus components
++++++++++++++++++++++++++++++++++++++++++++++++
Once we have bootstrapped our CLC, we have all the pre-requisites we need in order to provision all the rest of the
Eucalyptus components. The provision step will deploy all of these components in parallel. When all the components have
been provisioned a final configuration step will be run on the CLC in order to complete the installation as specified in
your environment file.

.. code-block:: console

    # calyptos provision -e my-environment.yml