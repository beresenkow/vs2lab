"""
Client and server using classes
"""

import logging
import socket

import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))

    tel_dictionary = {

        "Alice": "+49 151 23456789",
        "Bob": "+49 152 98765432",
        "Charlie": "+49 160 11122233",
        "David": "+49 171 44455566",
        "Eva": "+49 172 77788899",
        "Frank": "+49 173 33344455",
        "Grace" : "+49 174 66677788",
        "Hannah": "+49 175 99900011",
        "Ivan": "+49 176 55566677",
        "Julia": "+49 177 88899900"
            
    }

    def serve(self):
        """ Serve echo """
        self.sock.listen(1)
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                while True:  # forever
                    data = connection.recv(1024)  # receive data from client
                    if data == tel_dictionary["Alice"]:
                        connection.send(data + "*".encode('ascii')) 
                    if not data:
                        break  # stop if client stopped
                    connection.send(data + "*".encode('ascii'))  # return sent data plus an "*"
                connection.close()  # close the connection
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")


class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def call(self, msg_in="Hello, world"):
        """ Call server """
        self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        print(msg_out)  # print the result
        self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out
    
    def get(self, name_msg_in):
        self.sock.send(name_msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        tel_number = data.decode
        print(tel_number)
        self.sock.close()
        self.logger.info("Telephone number send")
        return tel_number

    def getall(self):
        #self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        tel_dictionary = data.decode
        print(tel_dictionary(["tel_number"]))
        self.sock.close()
        self.logger.info("Telephone number send")
        return tel_dictionary


    def close(self):
        """ Close socket """
        self.sock.close() #test

