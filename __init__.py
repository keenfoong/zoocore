import sys
import traceback

import zmq
import json
# sys.argv[-1] = "client"
# if sys.argv[-1] == "client":
#     print "client is going to send"
#     reqsock = zmq.Context().socket(zmq.REQ)
#     reqsock.connect("tcp://127.0.0.1:5555")
#     reqsock.send("hello from client")
#     recv = reqsock.recv()
#     print "Client received", recv, "exiting"
# else:
#     print "server is listening"
#     reqsock = zmq.Context().socket(zmq.REP)
#     reqsock.bind("tcp://127.0.0.1:5555")
#     recv = reqsock.recv()
#     print "server recieved", recv
#     reqsock.send("hello from server")
#     print "Server sent, exiting"


# sock = zmq.Context().socket(zmq.REP)
# sock.bind("tcp://127.0.0.1:5555")
# while True:
#     request = json.loads(sock.recv())
#     func, args = request
#     a, b = args
#     response = 0
#     try:
#         if func == "+":
#             response = a+b
#             code = 1
#         elif func == "-":
#             response = a-b
#             code = 1
#         else:
#             code = 2
#             response = "Invalid method {}".format(func)
#
#     except Exception:
#         code = 3
#         response = "".join(traceback.format_exc())
#     finally:
#         pickled = json.dumps([code, response])
#         sock.send(pickled)
