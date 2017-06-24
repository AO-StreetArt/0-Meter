.. _index:

0-Meter
=======

0-Meter is heavily influenced by JMeter, and is designed to be a load testing application for 0MQ-Based Applications.

The python program can read from flat files to build messages, as well as substitute variables found in a CSV file.  It can transmit one or more messages to a server all at once, or at scheduled intervals.

The execution of the program is driven by a configuration file, which is read at startup.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   pages/quickstart.rst
   pages/configuration.rst

Features
--------

* Send a single 0MQ Request Message with content from a flat file
* Send a set of 0MQ Request Messages with content from a set of flat files contained in a folder
* Send a set of 0MQ Request Messages with base content from a flat file, and variables substituted from a CSV file
* Send a set of 0MQ Request Messages, with content from files in a folder of generated from a CSV, scheduled periodically over a specified interval of time.
* Parse Responses and print to CSV or exit with error code based on results
