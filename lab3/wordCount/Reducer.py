import zmq
import threading

import constPipe as const

class Reducer(threading.Thread):
    def __init__(self):
        threading.__init__(self)