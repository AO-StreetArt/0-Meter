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
"""

import sys
import logging
import csv
import os

from ..Utils import select_files_in_folder, touch

# Populate the Base Message Global Variable
def build_msg(msg_path):
    #Open the base message File
    msg = None
    try:
        with open(msg_path, 'r') as f:
            msg = f.read()
            logging.debug("Base Message file opened")
    except Exception as e:
        logging.error('Exception during read of base message')
        logging.error(e)
    return msg


# Build a message list from a CSV
def build_msg_list_from_csv(msg, config_csv, csv_var_start, csv_var_end):

    logging.debug("Building message list from base message and csv")

    message_list = []

    #Open the CSV File and start building Message Files
    csvfile = None
    if sys.version_info[0] < 3:
        csvfile = open(config_csv, 'rb')
    else:
        csvfile = open(config_csv, 'r')
    logging.debug('CSV File Opened')
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')

    if sys.version_info[0] < 3:
        header_row = reader.next()
    else:
        header_row = reader.__next__()
    header_dict = {}
    logging.debug("Header row retrieved")

    for row in reader:
        repl_dict = {}
        for i in range(0, len(row)):
            logging.debug("Processing CSV Element: %s" % row[i])
            new_dict_key = "%s%s%s" % (csv_var_start, header_row[i], csv_var_end)
            repl_dict[new_dict_key] = row[i]
        message_list.append(replace_variables(msg, repl_dict))
    return message_list

# Replace a a set of variables within a message
# base_text - The message contianing variables
# variable_dict - A dictionary of variable names & values
def replace_variables(msg, variable_dict):
    # The dict uses different functions to return list generators of key/value pairs in 2.x vs 3.x
    # So, we use the sys module to detect at run time and use the correct method
    if sys.version_info[0] < 3:
        for key, val in variable_dict.iteritems():
            logging.debug("Replacing Variable %s with Value %s" % (key, val))
            msg = msg.replace(key, val)
    else:
        for key, val in variable_dict.items():
            logging.debug("Replacing Variable %s with Value %s" % (key, val))
            msg = msg.replace(key, val)
    return msg

# Pass in a Session as input and output a session that has been updated
def generate_msg_list(session):
    #Now, we need to determine how many messages we're sending and build them
    if session['single_message']:
        logging.debug("Building Single Message")
        session.num_msg=1
        session.base_msg = build_msg( os.path.abspath(session['msg_location']) )
        session.msg_list.append( session.base_msg )
    elif session['multi_message'] and session['include_csv']:
        logging.debug("Building Messages from CSV")
        #Pull the correct file paths
        msg_path = os.path.abspath(session['msg_location'])
        config_csv = os.path.abspath(session['csv_location'])
        session.base_msg = build_msg(msg_path)
        logging.debug("Base Message: %s" % session.base_msg)

        #Read the CSV, Build the message list, and take it's length for num_msg
        session.msg_list = build_msg_list_from_csv(session.base_msg, config_csv, session['csv_var_start'], session['csv_var_end'])
        session.num_msg=len(session.msg_list)

    elif session['multi_message']:
        logging.debug("Building Messages from Folder")
        msg_folder = select_files_in_folder(os.path.abspath(session['msg_folder_location']), session['msg_extension'])

        #Build the message list
        for path in msg_folder:
            session.msg_list.append( build_msg(os.path.abspath(path)) )
        session.num_msg = len(session.msg_list)
    return session
