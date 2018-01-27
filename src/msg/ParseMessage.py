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

import json
import logging
import sys
import os
import csv

from ..Utils import select_files_in_folder, touch

# Find a JSON Element within the specified doc, given the specified parsed path list
def find_json_path(json_doc, path_list):
    current_elt = json_doc
    # Iterate over the path_list to get to the element we want to match against
    for path_element in path_list:
        logging.debug("Entering Path Element %s -- %s" % (path_element[0], path_element[1]))
        try:
            if (path_element[0] == '.'):
                current_elt = current_elt[path_element[1]]
            elif (path_element[0] == '['):
                current_elt = current_elt[int(path_element[1])]
        except Exception as e:
            logging.error("Exception during retrieval of JSON Value")
            logging.error(e)
            sys.exit(1)
    return current_elt

def parse_responses(session):
    csvfile = None
    success_field_list = None
    success_key_list = None

    # Pull the paths for configured fields
    if session['fail_on_response']:
        success_field_list = session.parse_config_path(session['response_field_path'])
    if session['print_response_keys']:
        success_key_list = session.parse_config_path(session['response_key_path'])

        # Set up the CSV File
        if sys.version_info[0] < 3:
            csvfile = open(session['response_output_csv'], 'wb')
        else:
            csvfile = open(session['response_output_csv'], 'w')
        csvwriter = csv.writer(csvfile, delimiter=',',
                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['Key'])

    # Iterate over the responses
    for response in session.response_list:
        # JSON Response Parsing
        if (session['msg_extension'] == 'json'):
            logging.debug("Parsing Response: %s" % response)
            parsed_json = None
            try:
                parsed_json = json.loads(response)
            except Exception as e:
                try:
                    parsed_json = json.loads(response[1:])
                except Exception as e:
                    logging.error('Unable to parse response: %s' % response)
            if parsed_json is not None:

                # Write the response key to the CSV
                if session['print_response_keys']:
                    key_val = find_json_path(parsed_json, success_key_list)
                    try:
                        csvwriter.writerow([key_val])
                    except Exception as e:
                        logging.error("Exception while writing response key")
                        logging.error(e)
                        sys.exit(1)

                # Test the success value and exit if necessary
                if session['fail_on_response']:
                    try:
                        success_val = find_json_path(parsed_json, success_field_list)
                        logging.debug("Checking json success value")
                        if int(success_val) != int(session['response_success_value']):
                            logging.error("Incorrect Success value: %s != %s" % (success_val, session['response_success_value']))
                            sys.exit(1)
                    except Exception as e:
                        logging.error("Exception while comparing response success value")
                        logging.error(e)
                        sys.exit(1)
    if csvfile is not None:
        csvfile.close()
