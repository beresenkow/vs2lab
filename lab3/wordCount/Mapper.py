import zmq
import threading

import constPipe

class Mapper(threading.Thread):
    def __init__(self):
        threading.__init__(self)