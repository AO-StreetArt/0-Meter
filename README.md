# 0-Meter

0-Meter is heavily influenced by JMeter, and is designed to be a load testing application for 0MQ-Based Applications.

The python program can read from flat files to build messages, as well as substitute variables found in a CSV file.  It can transmit one or more messages to a server all at once, or at scheduled intervals.

The execution of the program is driven by a configuration file, which is read at startup.  Details are given below on the file.

## Features
* Send a single 0MQ Request Message with content from a flat file
* Send a set of 0MQ Request Messages with content from a set of flat files contained in a folder
* Send a set of 0MQ Request Messages with base content from a flat file, and variables substituted from a CSV file
* Send a set of 0MQ Request Messages, with content from files in a folder of generated from a CSV, scheduled periodically over a specified interval of time.

## Dependencies

Before downloading 0-Meter, you will need a few things installed:

* Python 2.7 - Can be downloaded [here] (https://www.python.org/)
* pyzmq
* apscheduler

Once you download Python, you can run the below commands to install the other dependencies:

`sudo pip install apscheduler`

`sudo pip install pyzmq`

## Use

0-Meter is designed to be easy to use.  It is a command line python script, and all of the software is contained within the .py file.  This only has a few dependencies to resolve, which can be found above in the 'Dependencies' segment.

Once the dependencies are installed, using the script is as easy as running the below command:

`python 0-meter.py config.xml`

The configuration XML will vary based on which XML you use, this command will work for the configuration XML provided

## Configuration

### Overview

Configuration of 0-Meter is done via editing of the configuration XML.  This file contains a number of fields critical to 0-Meter's execution, all of which are described below.

This methodology of configuration was selected to allow for 0-Meter to be run in a headless environment.  If a User Interface is desired, development of one would be easy so long as it simply wrote configuration XML files and then the python script can be executed independently.

Example Configuration Files can be found in the repository as well.

### Segments

There are four segments to the Configuration XML.

* Behavior - This fundamentally drives the behavior of the program
* Message - This drives how we generate messages to send
* ZeroMQ - Connectivity Information for ZeroMQ
* Logging - Logging Information

### Suggested Configurations

Suggested Configurations include True/False flags for Behavior Segment.  It also includes descriptions for required elements in the Message Segment.

All configurations require valid entries for all elements in both ZeroMQ and Logging Segments.

#### Send One Message from a Flat File

- [x] Single_Message
- [] Multi_Message
- [] Include_CSV
- [] Span_Over_Interval

Here we send a single message, read from a flat file, on the specified port.  The below values are read from the Message Segment:

* Message_Location - The filename & location of the message being sent

#### Send A Collection of Messages from Flat Files in a Folder

- [] Single_Message
- [x] Multi_Message
- [] Include_CSV
- [] Span_Over_Interval

Here we send a collection of messages, all at once, read from a collection of flat files in a folder, on the specified port.  The below values are read from the Message Segment:

* Message_Folder_Location - The location of the folder containing the messages being sent
* Message_Extension - The extension to look for in the specified file for messages

#### Send A Collection of Messages from Flat Files in a Folder, Scheduled over a specified interval of time

- [] Single_Message
- [x] Multi_Message
- [] Include_CSV
- [x] Span_Over_Interval

Here we send a collection of messages, all at once, read from a collection of flat files in a folder, on the specified port. These messages are sent periodically, with the formula being one message per (number_of_messages / interval) seconds. The below values are read from the Message Segment:

* Message_Folder_Location - The location of the folder containing the messages being sent
* Message_Extension - The extension to look for in the specified file for messages
* Interval - The overall interval for messages to be sent

#### Send A Collection of Messages from a Flat File & CSV

- [] Single_Message
- [x] Multi_Message
- [x] Include_CSV
- [] Span_Over_Interval

Here we send a collection of messages, all at once, on the specified port.  The messages are created by reading a base message, parsing it for defined variables, and substiting them with values from the CSV.  Variables are simply names that match the headers of the CSV File, starting with the Variable_Start_Character and ending with the Variable_End_Character.  The below values are read from the Message Segment:

* Message_Location - The location of the base message
* CSV_Location - The location & Filename of the CSV to read for variable data
* Variable_Start_Character - The start character of variables in the CSV
* Variable_End_Character - The end character of variables in the CSV

#### Send A Collection of Messages from a Flat File & CSV, Scheduled over a specified interval of time

- [] Single_Message
- [x] Multi_Message
- [x] Include_CSV
- [x] Span_Over_Interval

Here we send a collection of messages, all at once, on the specified port.  The messages are created by reading a base message, parsing it for defined variables, and substiting them with values from the CSV.  Variables are simply names that match the headers of the CSV File, starting with the Variable_Start_Character and ending with the Variable_End_Character.  These messages are sent periodically, with the formula being one message per (number_of_messages / interval) seconds.  The below values are read from the Message Segment:

* Message_Location - The location of the base message
* CSV_Location - The location & Filename of the CSV to read for variable data
* Variable_Start_Character - The start character of variables in the CSV
* Variable_End_Character - The end character of variables in the CSV
* Interval - The overall interval for messages to be sent

## To-Do List
* Batch message generation process to allow for larger-scale load testing.
* Add Google Protocol Buffer support & Serialization support to allow for serialized objects to be sent via 0MQ
