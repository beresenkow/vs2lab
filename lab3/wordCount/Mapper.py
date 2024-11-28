import zmq
import threading

import constPipe as const

class Mapper(threading.Thread):
    def __init__(self):
        threading.__init__(self)

    def run(self):
        context = zmq.Context()

        splitterSocket = context.socket(zmq.PULL)
        splitterSocket.bind("tcp://*" + const.PORT1)

        reducer1Socket = context.socket(zmq.PUSH)
        reducer1Socket.bind("tcp://*" + const.PORT2)

        reducer2Socket = context.socket(zmq.PUSH)
        reducer2Socket.bind("tcp://*" + const.PORT3)

        while True:
            sentence = splitterSocket.recv().decode('UTF-8')
            sentence = str.lower(sentence)

            words = str.split(sentence, ' ')

            for word in words:
                if word[0] < 'm':
                    reducer1Socket.send_string(word)
                else:
                    reducer2Socket.send_string(word)
