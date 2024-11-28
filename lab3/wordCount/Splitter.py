import zmq
import threading

import constPipe

class Splitter(threading.Thread):
    def __init__(self):
        threading.__init__(self)