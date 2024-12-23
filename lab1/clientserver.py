"""
Client and server using classes
"""

import logging
import socket

import const_cs
from context import lab_logging
import re

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True

    patternGET = r'^GET\s.*$'  # Pattern to match GET ...
    patternGETALL = r'^GETALL'  # Pattern to match GETALL

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))
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
            "Julia": "+49 177 88899900",
            "Ölaf": "+4753845678347509"
        }
        self._logger.info("Contacts dictionary initialized")

    def serve(self):
        """ Serve echo """
        self.sock.listen(1)
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                while True:  # forever
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                        break  # stop if client stopped

                    # Handle the request
                    response = self.handle_request(data.decode('utf-8'))
                    
                    # Send response back to the client
                    connection.send(response.encode('utf-8'))  # return sent data plus an "*"

                connection.close()  # close the connection
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")

    def handle_request(self, request):
        """Handle different requests"""
        if re.match(Server.patternGETALL, request):
            self._logger.info("Recieved GETALL request")
            contact_info = ', '.join([f'{name}: {number}' for name, number in self.tel_dictionary.items()])
            return contact_info
        elif re.match(Server.patternGET, request):
            self._logger.info("Recieved GET request")
            trimmed_data = request.strip()
            name = trimmed_data.split()[-1].strip()

            if name in self.tel_dictionary:
                return self.tel_dictionary[name]
            else:
                return f"Number not found for: {name}"
        else:
            self._logger.info("Unexpected request format")
            return request + "*"  # return sent data plus an "*"

class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def call(self, msg_in="Hello, world"):
        """ Call server """
        self.sock.send(msg_in.encode('utf-8'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('utf-8')
        print(msg_out)  # print the result
        self.logger.info("Client request handled.")
        return msg_out
    
    
    def get(self, name=""):
        return self.call(f"GET {name}")
    
    def getall(self):
        return self.call("GETALL")

    def close(self):
        """ Close socket """
        self.sock.close()
        self.logger.info("Client socket closed.")