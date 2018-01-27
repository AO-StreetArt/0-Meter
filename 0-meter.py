"""
MIT License Block

Copyright (c) 2015 Alex Barry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

-----------------------------------------------------------------------------

0-Meter is a configurable load testing framework for 0MQ-Based
Messaging Applications.

It reads from a configuration XML to determine how to proceed with test cases

We support sending an individual file as well as defining variables and
updating values with those from a separate CSV.

@author: alex barry
"""

import sys
import logging
import zmq
import os
import csv
import json
import time

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
except Exception as e:
    print('Unable to load scheduling libraries due to error:')
    print(e)

try:
    from kafka import KafkaConsumer
except Exception as e:
    print('Unable to load Kafka libraries due to error:')
    print(e)

from src.session.Session import Session
from src.msg.BuildMessage import generate_msg_list
from src.msg.ParsingStream import ParsingStream
from src.Utils import select_files_in_folder, touch

# Define the single global session
session = None
parsing_stream = None

# Post a message from the global variable list to the global socket
# When messages are sent on a scheduled interval, this is called on a
# background thread
def post_message():
    global parsing_stream
    global session
    if len(session.msg_list) > 0:
        try:
            #Send the message
            msg = session.msg_list.pop(0)
            session.time_list.append(time.time())
            session.socket.send_string(msg + "\n")
            logging.info("Message sent:")
            logging.info(msg)

            if session['out_0mq_connect_type'] == "REQ":
                #Recieve the response
                resp = session.socket.recv()
                session.response_list.append(resp)
                session.resp_time_list.append(time.time())
                logging.info("Response Recieved:")
                logging.info(resp)
                # Apply any parsing rules and print the response
                if parsing_stream is not None:
                    parsing_stream.stream_message(resp)
        except Exception as e:
            print("Error sending")
            logging.error('Exception')
            logging.error(e)
            del session.msg_list[:]
            session.socket.close()
            sys.exit(1)


# Execute the main function and start 0-meter
def execute_main(config_file):
    global parsing_stream
    global session
    session = Session()

    # Set up the session
    session.configure(config_file)

    #Set up the file logging config
    if session['log_level'] == 'Debug':
        logging.basicConfig(filename=session['log_file'], level=logging.DEBUG)
    elif session['log_level'] == 'Info':
        logging.basicConfig(filename=session['log_file'], level=logging.INFO)
    elif session['log_level'] == 'Warning':
        logging.basicConfig(filename=session['log_file'], level=logging.WARNING)
    elif session['log_level'] == 'Error':
        logging.basicConfig(filename=session['log_file'], level=logging.ERROR)
    else:
        print("Log level not set to one of the given options, defaulting to debug level")
        logging.basicConfig(filename=session['log_file'], level=logging.DEBUG)

    try:
        #Attempt to connect to the outbound ZMQ Socket
        logging.debug("Attempting to connect to outbound 0MQ Socket with connection:")
        logging.debug(session['out_0mq_connect'])
        session.context = zmq.Context()
        if (session['timeout'] > 0):
            session.context.setsockopt(zmq.RCVTIMEO, session['timeout'])
            session.context.setsockopt(zmq.LINGER, 0)
        if session['out_0mq_connect_type'] == "REQ":
            session.socket = session.context.socket(zmq.REQ)
            session.socket.connect(session['out_0mq_connect'])
        elif session['out_0mq_connect_type'] == "PUB":
            socket = context.socket(zmq.PUB)
            socket.connect(session['out_0mq_connect'])
        else:
            logging.error("Unknown Connection Type encountered")
            sys.exit(1)
    except Exception as e:
        logging.error('Exception')
        logging.error(e)
        print("Exception encountered connecting to 0MQ Socket, please see logs for details")
        sys.exit(1)

    #Now, we need to determine how many messages we're sending and build them
    session = generate_msg_list(session)

    # Build the parsing stream, if necessary, to apply our parsing rules and
    # print output
    if session['parse_responses']:
        rule_list = []
        if session['fail_on_response']:
            rule_list.append('Success_Validation')
        parsing_stream = ParsingStream(rule_list, session)

    if session['connect_to_kafka']:
        kafka_consumer = KafkaConsumer(session['kafka_topic'], bootstrap_servers=session['kafka_address'])

    #Now, we can execute the test plan
    if session['span_interval'] == False:
        logging.debug("Sending Messages all at once")
        while len(session.msg_list) > 0:
            post_message()
    else:
        logging.debug("Set up the Background Scheduler")
        scheduler = BackgroundScheduler()
        time_interv = num_msg / session['interval']
        logging.debug("Interval: %s" % (time_interv))
        interv = IntervalTrigger(seconds=time_interv)
        scheduler.add_job(post_message, interv)
        scheduler.start()
        time.sleep(session['interval'])

    # Look for a message in Kafka
    # Connect to Kafka
    if session['connect_to_kafka']:
        counter = 0
        for kafka_msg in kafka_consumer:
            counter += 1
            if session['print_kafka_output']:
                logging.info(kafka_msg)
        if session['expect_kafka_output'] and counter == 0:
            print("No Kafka Output Found, but expected")
            logging.error("No Kafka Output Found, but expected")
            sys.exit(1)

    return 0;


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Input Parameters:")
        print("Configuration File: The file name of the Configuration XML")
        print("Example: python 0-meter.py config.xml")
    elif len(sys.argv) != 2:
        print("Wrong number of Input Parameters")
    else:
        print("Input Parameters:")
        print("Configuration File: %s" % (sys.argv[1]))
    execute_main(sys.argv[1])
