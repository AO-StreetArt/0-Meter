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
import sys
from src.msg.ParseMessage import find_json_path
from ..Utils import get_exception

class ParsingRule(object):
    def __init__(self, name):
        self._name = name

    # Should be overriden by each individual rule class
    # Accept a parsed JSON Message
    def assert_on_message(self, msg):
        pass

    def get_name(self):
        return self._name

class SuccessValidationRule(ParsingRule):
    def __init__(self, success_field_list, response_success_value):
        ParsingRule.__init__(self, "Success_Validation")
        self._success_field_list = success_field_list
        self._response_success_value = response_success_value

    def assert_on_message(self, msg):
        try:
            success_val = find_json_path(msg, self._success_field_list)
            logging.debug("Checking json success value")
            if int(success_val) != int(self._response_success_value):
                logging.error("Incorrect Success value: %s != %s" % (success_val, self._response_success_value))
                sys.exit(1)
        except Exception as e:
            logging.error("Exception while comparing response success value")
            logging.error(e)
            logging.error(get_exception())
            sys.exit(1)
