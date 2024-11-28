import zmq
import threading

import constPipe as const

class Mapper(threading.Thread):
    def __init__(self):
        threading.__init__(self)