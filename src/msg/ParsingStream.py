"""
MIT License Block

Copyright (c) 2017 Alex Barry

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
import logging
import json
import sys
import csv
from ..Utils import get_exception

from src.msg.ParsingRules import SuccessValidationRule
from src.msg.ParseMessage import find_json_path

class ParsingStream(object):
    def __init__(self, rule_list, session):
        self._print_response_keys = session['print_response_keys']
        self._success_field_list = None
        self._success_key_list = None

        # Pull the paths for configured fields
        if session['fail_on_response']:
            self._success_field_list = session.parse_config_path(session['response_field_path'])
        if session['print_response_keys']:
            self._success_key_list = session.parse_config_path(session['response_key_path'])

            # Set up the CSV File
            if sys.version_info[0] < 3:
                self._csvfile = open(session['response_output_csv'], 'wb')
            else:
                self._csvfile = open(session['response_output_csv'], 'w')
            self._csvwriter = csv.writer(self._csvfile, delimiter=',',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
            self._csvwriter.writerow(['Key'])

        # Set up the Rule List
        self._rule_list = []

        # Set up the Success Validation Rule
        if session['fail_on_response']:
            success_rule = SuccessValidationRule(self._success_field_list, session['response_success_value'])
            for rule in rule_list:
                if rule == success_rule.get_name():
                    self._rule_list.append(success_rule)

    def stream_message(self, msg):
        logging.debug("Parsing Response: %s" % msg)
        parsed_json = None
        try:
            parsed_json = json.loads(msg)
        except Exception as e:
            try:
                parsed_json = json.loads(msg[1:])
            except Exception as e:
                logging.error('Unable to parse response')
                logging.error(e)
                logging.error(get_exception())

        if parsed_json is not None:
            # Write the response key to the CSV
            if self._print_response_keys:
                key_val = find_json_path(parsed_json, self._success_key_list)
                try:
                    self._csvwriter.writerow([key_val])
                except Exception as e:
                    logging.error("Exception while writing response key")
                    logging.error(e)
                    sys.exit(1)
            # Execute the necessary rules
            for rule in self._rule_list:
                rule.assert_on_message(parsed_json)

    def close(self):
        if self._csvfile is not None:
            self._csvfile.close()
