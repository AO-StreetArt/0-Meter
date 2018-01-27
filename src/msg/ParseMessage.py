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

import logging
import sys
import os

from ..Utils import get_exception

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
            logging.error(path_list)
            logging.error(e)
            logging.error(get_exception())
            sys.exit(1)
    return current_elt
