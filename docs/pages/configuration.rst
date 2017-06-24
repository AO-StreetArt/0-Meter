.. _configuration:

=============
Configuration
=============

:ref:`Go Home <index>`

Overview
--------

Configuration of 0-Meter is done via editing of the configuration XML.  This file contains a number of fields critical to 0-Meter's execution, all of which are described below.

This methodology of configuration was selected to allow for 0-Meter to be run in a headless environment.  If a User Interface is desired, development of one would be easy so long as it simply wrote configuration XML files and then the python script can be executed independently.

Example Configuration Files can be found in the repository as well.

There are five segments to the Configuration XML.

* Behavior - This fundamentally drives the behavior of the program
* Message - This drives how we generate messages to send
* ZeroMQ - Connectivity Information for ZeroMQ
* Logging - Logging Information
* Response - Response Parser configuration

0-Meter has a response parser which can be configured independently of the sender, suggested configurations for both are supplied below.  Suggested Configurations include True/False flags for Behavior Segment.  It also includes descriptions for required elements in the Message Segment.

All configurations require valid entries for all elements in both ZeroMQ and Logging Segments.

Suggested Response Parser Configurations
----------------------------------------

Parse Responses and Fail on a Failure Response
----------------------------------------------

- [x] Parse_Responses
- [] Print_Response_Keys
- [x] Fail_On_Response

0-Meter can be configured to fail when receiving a response which does not match a specified value.  The below values are read from the Response Segment:

* Field_Path - The :ref:`field_paths` string which is used to determine what field in the response is compared against.
* Success_Value - The value to compare against for the field specified

Parse Responses and Write Keys to CSV
-------------------------------------

- [x] Parse_Responses
- [x] Print_Response_Keys
- [] Fail_On_Response

0-Meter can be configured to print values from the response message.  The below values are read from the Response Segment:

* Key_Path - The :ref:`field_paths` string which is used to determine what field in the response is written to the CSV
* Output_Csv - The name of the CSV file to create with the response keys


Suggested Sender Configurations
-------------------------------

Send One Message from a Flat File
---------------------------------

- [x] Single_Message
- [] Multi_Message
- [] Include_CSV
- [] Span_Over_Interval

Here we send a single message, read from a flat file, on the specified port.  The below values are read from the Message Segment:

* Message_Location - The filename & location of the message being sent

Send A Collection of Messages from Flat Files in a Folder
---------------------------------------------------------

- [] Single_Message
- [x] Multi_Message
- [] Include_CSV
- [] Span_Over_Interval

Here we send a collection of messages, all at once, read from a collection of flat files in a folder, on the specified port.  The below values are read from the Message Segment:

* Message_Folder_Location - The location of the folder containing the messages being sent
* Message_Extension - The extension to look for in the specified file for messages

Send A Collection of Messages from Flat Files in a Folder, Scheduled over a specified interval of time
------------------------------------------------------------------------------------------------------

- [] Single_Message
- [x] Multi_Message
- [] Include_CSV
- [x] Span_Over_Interval

Here we send a collection of messages, all at once, read from a collection of flat files in a folder, on the specified port. These messages are sent periodically, with the formula being one message per (number_of_messages / interval) seconds. The below values are read from the Message Segment:

* Message_Folder_Location - The location of the folder containing the messages being sent
* Message_Extension - The extension to look for in the specified file for messages
* Interval - The overall interval for messages to be sent

Send A Collection of Messages from a Flat File & CSV
----------------------------------------------------

- [] Single_Message
- [x] Multi_Message
- [x] Include_CSV
- [] Span_Over_Interval

Here we send a collection of messages, all at once, on the specified port.  The messages are created by reading a base message, parsing it for defined variables, and substituting them with values from the CSV.  Variables are simply names that match the headers of the CSV File, starting with the Variable_Start_Character and ending with the Variable_End_Character.  The below values are read from the Message Segment:

* Message_Location - The location of the base message
* CSV_Location - The location & Filename of the CSV to read for variable data
* Variable_Start_Character - The start character of variables in the CSV
* Variable_End_Character - The end character of variables in the CSV

Send A Collection of Messages from a Flat File & CSV, Scheduled over a specified interval of time
-------------------------------------------------------------------------------------------------

- [] Single_Message
- [x] Multi_Message
- [x] Include_CSV
- [x] Span_Over_Interval

Here we send a collection of messages, all at once, on the specified port.  The messages are created by reading a base message, parsing it for defined variables, and substituting them with values from the CSV.  Variables are simply names that match the headers of the CSV File, starting with the Variable_Start_Character and ending with the Variable_End_Character.  These messages are sent periodically, with the formula being one message per (number_of_messages / interval) seconds.  The below values are read from the Message Segment:

* Message_Location - The location of the base message
* CSV_Location - The location & Filename of the CSV to read for variable data
* Variable_Start_Character - The start character of variables in the CSV
* Variable_End_Character - The end character of variables in the CSV
* Interval - The overall interval for messages to be sent

.. toctree::
   field_paths.rst
