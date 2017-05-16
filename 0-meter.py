# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 23:47:16 2016

-0-Meter Main Class-

0-Meter is a configurable load testing framework for 0MQ-Based
Messaging Applications.

It reads from a configuration XML to determine how to proceed with test cases

We support sending an individual file as well as defining variables and
updating values with those from a separate CSV.

@author: alex
"""

import xml.etree.ElementTree as ET
import sys
import logging
import zmq
import os
import csv

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
except Exception as e:
    print('Unable to load scheduling libraries due to error:')
    print(e)

import time

#Global Variables
msg_list = []
context = None
socket = None
num_msg = 0
base_msg = ""

#Global Variables for tracking response times
resp_time_list = []
time_list = []

def build_base_msg(msg_path):
    #Open the base message File
    global base_msg
    try:
        with open(msg_path, 'r') as f:
            global base_msg
            base_msg = f.read()
            logging.debug("Base Message file opened")
    except Exception as e:
        logging.error('Exception during read of base message')
        logging.error(e)

def build_msg_list_from_csv(msg_path, config_csv):

    global msg_list

    #List of replacement variables & values
    #We do not insert or remove, only append and clear which means we can assume
    #that they have the same ordering
    repl_variables = []
    repl_values = []

    #Counter variable
    file_id_counter=0
    row_counter=0
    char_counter=0

    #Open the base message File
    try:
        with open(msg_path, 'r') as f:
            msg_string = f.read()
            logging.debug("Base Message file opened")
    except Exception as e:
        logging.error('Exception during read of base message')
        logging.error(e)
        msg_string = ""

    #Open the CSV File and start building Message Files
    with open(config_csv, 'rb') as csvfile:
        logging.debug('CSV File Opened')
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            #We can access elements in the row with row[i], where i = column number
            #First Row is assumed to contain headers
            if row_counter==0:
                #This is a header row
                for element in row:
                    repl_variables.append(element)
                    logging.debug('Replacement Variable %s added' % (element))
            else:
                #Process the row and build a new Message

                #Populate the repl_values list
                for element in row:
                    repl_values.append(element)

                #Build the string message to be written to the output file
                new_str = msg_string

                str_length = len(new_str)
                while char_counter < str_length:
                    if new_str[char_counter] == csv_var_start:
                        #We have found a replacement variable
                        #We need to replace this block with the
                        #corresponding repl_value
                        logging.debug('Replacement variable found in base message')
                        var_start=char_counter
                        var_end=0
                        var_name=""
                        found_back=False
                        var_id=-1
                        while found_back==False and len(new_str) > char_counter:
                            logging.debug('Find full variable loop entered')
                            char_counter+=1
                            if new_str[char_counter] == csv_var_end:
                                found_back=True
                                var_end=char_counter
                                logging.debug('Var Start Position: %s' % (var_start))
                                logging.debug('Var End Position: %s' % (var_end))
                            else:
                                var_name = var_name + new_str[char_counter]
                                logging.debug('Character added: %s' % (new_str[char_counter]))
                        i=0
                        for i in range(0, len(repl_variables)):
                            if repl_variables[i] == var_name:
                                var_id=i

                        #We only want to perform a replacement if we found a matching variable name
                        if var_id > -1:
                            new_str = new_str[:var_start] + repl_values[var_id] + new_str[var_end+1:]
                            str_length = len(new_str)
                            char_counter=var_start

                        logging.debug('Character Counter')
                    else:
                        char_counter+=1

                msg_list.append(new_str)

                #Clear the repl_values array for the next iteration
                del repl_values[:]

                #Zero out the character counter for the next iteration
                char_counter=0

                #Iterate the file counter
                file_id_counter+=1

            row_counter+=1

def select_files_in_folder(dir, ext):
    for file in os.listdir(dir):
        if file.endswith('.%s' % ext):
            yield os.path.join(dir, file)

def touch(file_path):
    open(file_path, 'a').close()


def post_message():
    global resp_time_list
    global time_list
    global msg_list
    global socket
    if len(msg_list) > 0:
        #Send the message
        msg = msg_list.pop(0)
        time_list.append(time.time())
        socket.send_string(msg)
        logging.info("Message sent:")
        logging.info(msg)

        #Recieve the response
        try:
            resp = socket.recv()
            resp_time_list.append(time.time())
            logging.info("Response Recieved:")
            logging.info(resp)
        except Exception as e:
            print("Socket Timeout")
            del msg_list[:]
            socket.close()
            sys.exit(1)
    else:
        sys.exit(1)


def execute_main():
    global base_msg
    global msg_list
    global socket

    timeout = 1000

    if len(sys.argv) == 1:
        print("Input Parameters:")
        print("Configuration File: The file name of the Configuration XML")
        print("Example: python 0-meter.py config.xml")
    elif len(sys.argv) != 2:

        print("Wrong number of Input Parameters")

    else:

        print("Input Parameters:")
        print("Configuration File: %s" % (sys.argv[1]))

    #-----------------------------------------------------------------------------#
    #-----------------------------------------------------------------------------#

        single_message = False
        multi_message = False
        include_csv = False
        span_interval = False

        msg_location = ""
        msg_folder_location = ""
        msg_extension = ""
        interval = 5
        csv_location = ""
        csv_var_start = ""
        csv_var_end = ""
        out_0mq_connect = ""
        out_0mq_connect_type = ""
        timeout = 1000
        log_file = ""
        log_level = ""

        #Parse the config XML and pull the values

        tree = ET.parse(sys.argv[1])
        root = tree.getroot()
        for element in root:
            if element.tag == 'Behavior':
                for param in element:
                    if param.tag == 'Single_Message':
                        if param.text == 'True':
                            single_message = True
                    if param.tag == 'Multi_Message':
                        if param.text == 'True':
                            multi_message = True
                    if param.tag == 'Include_CSV':
                        if param.text == 'True':
                            include_csv = True
                    if param.tag == 'Span_Over_Interval':
                        if param.text == 'True':
                            span_interval = True
            if element.tag == 'Message':
                for param in element:
                    if param.tag == 'Message_Location':
                        msg_location = param.text
                    if param.tag == 'Message_Folder_Location':
                        msg_folder_location = param.text
                    if param.tag == 'Message_Extension':
                        msg_extension = param.text
                    if param.tag == 'Interval':
                        interval = float(param.text)
                    if param.tag == 'CSV_Location':
                        csv_location = param.text
                    if param.tag == 'Variable_Start_Character':
                        csv_var_start = param.text
                    if param.tag == 'Variable_End_Character':
                        csv_var_end = param.text
            if element.tag == 'ZeroMQ':
                for param in element:
                    if param.tag == 'Outbound_Connection':
                        out_0mq_connect = param.text
                    if param.tag == 'Outbound_Connection_Type':
                        out_0mq_connect_type = param.text
                    if param.tag == "Timeout":
                        timeout = int(float(param.text))
            if element.tag == 'Logging':
                for param in element:
                    if param.tag == 'Log_File':
                        log_file = param.text
                    elif param.tag == 'Log_Level':
                        log_level = param.text

        #Set up the file logging config
        if log_level == 'Debug':
            logging.basicConfig(filename=log_file, level=logging.DEBUG)
        elif log_level == 'Info':
            logging.basicConfig(filename=log_file, level=logging.INFO)
        elif log_level == 'Warning':
            logging.basicConfig(filename=log_file, level=logging.WARNING)
        elif log_level == 'Error':
            logging.basicConfig(filename=log_file, level=logging.ERROR)
        else:
            print("Log level not set to one of the given options, defaulting to debug level")
            logging.basicConfig(filename=log_file, level=logging.DEBUG)

        try:
            #Attempt to connect to the outbound ZMQ Socket
            logging.debug("Attempting to connect to outbound 0MQ Socket with connection:")
            logging.debug(out_0mq_connect)
            context = zmq.Context()
            context.setsockopt(zmq.RCVTIMEO, timeout)
            context.setsockopt(zmq.LINGER, 0)
            if out_0mq_connect_type == "REQ":
                socket = context.socket(zmq.REQ)
                socket.connect(out_0mq_connect)
            elif out_0mq_connect_type == "PUB":
                socket = context.socket(zmq.PUB)
                socket.connect(out_0mq_connect)
            else:
                logging.error("Unknown Connection Type encountered")
                return 0

        #If an exception is thrown while executing the tests,
        #write that out to the log file
        except Exception as e:
            logging.error('Exception')
            logging.error(e)
            print("Exception encountered connecting to 0MQ Socket, please see logs for details")
            return 0

        #Now, we need to determine how many messages we're sending and build them
        if single_message:
            logging.debug("Building Single Message")
            num_msg=1
            build_base_msg(os.path.abspath(msg_location))
            msg_list.append(base_msg)
        elif multi_message == True and include_csv == True:
            logging.debug("Building Messages from CSV")
            #Pull the correct file paths
            msg_path = os.path.abspath(msg_location)
            config_csv = os.path.abspath(csv_location)

            #Read the CSV, Build the message list, and take it's length for num_msg
            build_msg_list_from_csv(msg_path, config_csv)
            num_msg=len(msg_list)

        elif multi_message:
            logging.debug("Building Messages from Folder")
            msg_folder = select_files_in_folder(os.path.abspath(msg_folder_location), msg_extension)

            #Build the message list
            for msg in msg_folder:
                build_base_msg(os.path.abspath(msg))
                msg_list.append(base_msg)

            num_msg = len(msg_list)

        #Now, we can execute the test plan
        if span_interval == False:
            logging.debug("Sending Messages all at once")
            total_count = 0
            while len(msg_list) > 0 and total_count < 10000:
                post_message()
                total_count+=1
        else:
            logging.debug("Set up the Background Scheduler")
            scheduler = BackgroundScheduler()
            time_interv = num_msg / interval
            logging.debug("Interval: %s" % (time_interv))
            interv = IntervalTrigger(seconds=time_interv)
            scheduler.add_job(post_message, interv)
            scheduler.start()
            time.sleep(interval)
    return 0;


if __name__ == "__main__":
    execute_main()
