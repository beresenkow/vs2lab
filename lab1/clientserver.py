"""
Client and server using classes
"""

import logging
import socket
import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # initialize logging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # set timeout to prevent indefinite blocking
        self._logger.info("Server bound to socket " + str(self.sock))

        # The dictionary containing telephone numbers
        self.tel_dictionary = {
            "Alice": "+49 151 23456789",
            "Bob": "+49 152 98765432",
            "Charlie": "+49 160 11122233",
            "David": "+49 171 44455566",
            "Eva": "+49 172 77788899",
            "Frank": "+49 173 33344455",
            "Grace": "+49 174 66677788",
            "Hannah": "+49 175 99900011",
            "Ivan": "+49 176 55566677",
            "Julia": "+49 177 88899900"
        }

    def serve(self):
        """ Serve requests from the client """
        self.sock.listen(1)
        while self._serving:  # continue serving as long as _serving is True
            try:
                (connection, address) = self.sock.accept()  # accepts new socket and client address
                self._logger.info(f"Connection established with {address}")
                while True:
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                        break  # stop if no data is received

                    request = data.decode('ascii')
                    response = self.tel_dictionary.get(request, "Name not found")  # get the number or "not found" message
                    connection.send(response.encode('ascii'))  # send response
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
        """ Send a basic message to the server and receive the response """
        self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        print(msg_out)  # print the result
        self.logger.info("Response received: " + msg_out)
        return msg_out

    def get(self, name):
        """ Request the telephone number for a given name """
        self.sock.send(name.encode('ascii'))  # send the name to the server
        data = self.sock.recv(1024)  # receive the response
        tel_number = data.decode('ascii')
        print(f"Telephone number for {name}: {tel_number}")
        self.logger.info(f"Telephone number for {name} received")
        return tel_number


    def getall(self):
        self.sock.send("getall".encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        tel_dictionary = data.decode
        print(tel_dictionary(["tel_number"]))
        self.sock.close()
        self.logger.info("Telephone number send")
        return tel_dictionary


    def close(self):
        """ Close socket """
        self.sock.close() #test

