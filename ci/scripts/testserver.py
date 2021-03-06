#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import logging
import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:1234")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)

    #  Send reply back to client
    socket.send_string('{"responses": [{"codes": [0, 1, 2], "msg": "Thanks!"}, {"codes": [3, 4, 5], "msg": "Not!"}]}')
