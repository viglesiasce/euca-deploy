.. Calyptos documentation master file, created by
   sphinx-quickstart on Mon May 11 15:52:37 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Calyptos' documentation!
===================================

.. WARNING::
   Calyptos is still under development for issues/feedback/improvements please go to the project's page
   on GitHub

Calyptos is a command line tool intended to help Eucalyptus cloud administrators with the following
phases of their Eucalyptus deployments:

* Configuration
* Deployment
* Getting Status
* Debugging
* Backup/Restore (Not yet implemented)

Each of the phases is implemented as plugins using the `stevedore library <http://docs.openstack.org/developer/stevedore/>`_.
This allows new validators, deployers and debuggers to be implemented with modularity in mind. For more information on
how to create your own plugins head over to the :doc:`plugin documentation <plugins>`.

Currently Calyptos supports deploying the following:

* Object Storage Backends

  * Walrus
  * RiakCS

* Network modes

  * EDGE
  * VPC (Midokura)
  * Managed No VLAN
  * Managed

* Storage backends

  * DAS
  * Overlay
  * Equallogic
  * Netapp
  * Ceph
  * EMC VNX

Contents
========

.. toctree::
   :maxdepth: 3

   quick-start
   configuration
   plugins

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

