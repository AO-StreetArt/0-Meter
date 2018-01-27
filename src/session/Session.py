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

import xml.etree.ElementTree as ET
import sys
import logging

class Session(object):
    def __init__(self):
        self.param_list = {}

        #Global Variables
        self.msg_list = []
        self.response_list = []
        self.context = None
        self.socket = None
        self.num_msg = 0
        self.base_msg = ""

        #Global Variables for tracking response times
        self.resp_time_list = []
        self.time_list = []

    def teardown(self):
        self.param_list.clear()

    def __len__(self):
        return len(self.param_list)

    def __getitem__(self, key):
        return self.param_list[key]

    def __setitem__(self, key, value):
        self.param_list[key] = value

    def __delitem__(self, key):
        del self.param_list[key]

    def __iter__(self):
        return iter(self.param_list)

    def configure(self, config_file):
        # Read the config file
        self.param_list['single_message'] = False
        self.param_list['multi_message'] = False
        self.param_list['include_csv'] = False
        self.param_list['span_interval'] = False

        self.param_list['msg_location'] = ""
        self.param_list['msg_folder_location'] = ""
        self.param_list['msg_extension'] = ""
        self.param_list['interval'] = 5
        self.param_list['csv_location'] = ""
        self.param_list['csv_var_start'] = ""
        self.param_list['csv_var_end'] = ""
        self.param_list['out_0mq_connect'] = ""
        self.param_list['out_0mq_connect_type'] = ""
        self.param_list['timeout'] = 0
        self.param_list['log_file'] = ""
        self.param_list['log_level'] = ""

        self.param_list['parse_responses'] = False
        self.param_list['print_response_keys'] = False
        self.param_list['fail_on_response'] = False
        self.param_list['response_field_path'] = ""
        self.param_list['response_success_value'] = ""
        self.param_list['response_output_csv'] = ""
        self.param_list['response_key_path'] = ""

        #Parse the config XML and pull the values
        tree = ET.parse(sys.argv[1])
        root = tree.getroot()
        for element in root:
            if element.tag == 'Behavior':
                for param in element:
                    if param.tag == 'Single_Message':
                        if param.text == 'True' or param.text == 'true':
                            self.param_list['single_message'] = True
                    if param.tag == 'Multi_Message':
                        if param.text == 'True' or param.text == 'true':
                            self.param_list['multi_message'] = True
                    if param.tag == 'Include_CSV':
                        if param.text == 'True' or param.text == 'true':
                            self.param_list['include_csv'] = True
                    if param.tag == 'Span_Over_Interval':
                        if param.text == 'True' or param.text == 'true':
                            self.param_list['span_interval'] = True
                    if param.tag == 'Parse_Responses':
                        if param.text == 'True' or param.text == 'true':
                            self.param_list['parse_responses'] = True
                    if param.tag == 'Print_Response_Keys':
                        if param.text == 'True' or param.text == 'true':
                            self.param_list['print_response_keys'] = True
                    if param.tag == 'Fail_On_Response':
                        if param.text == 'True' or param.text == 'true':
                            self.param_list['fail_on_response'] = True
            if element.tag == 'Message':
                for param in element:
                    if param.tag == 'Message_Location':
                        self.param_list['msg_location'] = param.text
                    if param.tag == 'Message_Folder_Location':
                        self.param_list['msg_folder_location'] = param.text
                    if param.tag == 'Message_Extension':
                        self.param_list['msg_extension'] = param.text
                    if param.tag == 'Interval':
                        self.param_list['interval'] = float(param.text)
                    if param.tag == 'CSV_Location':
                        self.param_list['csv_location'] = param.text
                    if param.tag == 'Variable_Start_Character':
                        self.param_list['csv_var_start'] = param.text
                    if param.tag == 'Variable_End_Character':
                        self.param_list['csv_var_end'] = param.text
            if element.tag == 'ZeroMQ':
                for param in element:
                    if param.tag == 'Outbound_Connection':
                        self.param_list['out_0mq_connect'] = param.text
                    if param.tag == 'Outbound_Connection_Type':
                        self.param_list['out_0mq_connect_type'] = param.text
                    if param.tag == "Timeout":
                        self.param_list['timeout'] = int(float(param.text))
            if element.tag == 'Logging':
                for param in element:
                    if param.tag == 'Log_File':
                        self.param_list['log_file'] = param.text
                    elif param.tag == 'Log_Level':
                        self.param_list['log_level'] = param.text
            if element.tag == 'Response':
                for param in element:
                    if param.tag == 'Field_Path':
                        self.param_list['response_field_path'] = param.text
                    if param.tag == 'Key_Path':
                        self.param_list['response_key_path'] = param.text
                    if param.tag == 'Success_Value':
                        self.param_list['response_success_value'] = param.text
                    if param.tag == 'Output_Csv':
                        self.param_list['response_output_csv'] = param.text

    def __str__(self):
        ret_str = "Session:\n"
        for key, val in self.param_list.iteritems():
            ret_str = ret_str + "%s: %s\n" % (key, val)
        return ret_str

    # Parse a configuration path in the format root.obj[1
    def parse_config_path(self, field_path):
        logging.debug("Entering Parsing of Response Field Path")
        # Parse the Field Path
        field_path_list = []
        # Pull the first value in assuming the message is an object
        cut_index = 0
        pd_index = field_path.find('.')
        ar_index = field_path.find('[')
        if pd_index < ar_index:
            cut_index = pd_index
        else:
            cut_index = ar_index
        path_list_tuple = None
        if cut_index > -1:
            path_list_tuple = ('.', field_path[0:cut_index])
            field_path_list.append(path_list_tuple)
            field_path = field_path[cut_index:]
        else:
            path_list_tuple = ('.', field_path)
            field_path_list.append(path_list_tuple)
            return field_path_list
        logging.debug("Writing first tuple to path list: %s -- %s" % (path_list_tuple[0], path_list_tuple[1]))
        while( True ):
            logging.debug("Parsing Iteration of Response Field Path, remaining field path: %s" % field_path)

            # Find the first delimiter
            cut_index = 0
            pd_index = field_path.find('.',1)
            ar_index = field_path.find('[',1)
            if pd_index > -1 and (pd_index < ar_index or ar_index < 0):
                cut_index = pd_index
            else:
                cut_index = ar_index

            # If another . or [ is found
            if cut_index > -1:
                path_list_tuple = (field_path[0:1], field_path[1:cut_index])
                field_path_list.append(path_list_tuple)
                field_path = field_path[cut_index:]
            else:
                path_list_tuple = (field_path[0:1], field_path[1:])
                field_path_list.append(path_list_tuple)
                break

        return field_path_list
