import zmq
import threading

import constPipe as const

class Reducer(threading.Thread):
    def __init__(self):
        threading.__init__(self)

    def run(self):
        context = zmq.Context()

        mapperSocket = context.socket(zmq.PULL)
        mapperSocket.bind(f"tcp://localhost:{self.port}")

        while True:
            word = mapperSocket.recv().decode('UTF-8')
            if word in self.words:
                self.words[word] += 1
            else:
                self.words[word] = 1

            print("Das Wort: '" + word + "' wurde empfangen und zwar ganze " + str(self.words[word]) + " mal.")
