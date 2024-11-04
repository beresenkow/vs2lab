"""
Simple client server unit test
"""

import logging
import threading
import unittest

import clientserver
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)


class TestEchoService(unittest.TestCase):
    """The test"""
    _server = clientserver.Server()  # create single server in class variable
    _server_thread = threading.Thread(target=_server.serve)  # define thread for running server

    @classmethod
    def setUpClass(cls):
        cls._server_thread.start()  # start server loop in a thread (called only once)

    def setUp(self):
        super().setUp()
        self.client = clientserver.Client()  # create new client for each test

    def test_srv_get(self):  # each test_* function is a test
        """Test simple call"""
        msg = self.client.call("Hello VS2Lab")
        self.assertEqual(msg, 'Hello VS2Lab*')

    def test_cl_get(self):
        """test get method"""
        tel_number = self.client.get("Alice")
        self.assertEqual(tel_number, "+49 151 23456789")

    def test_cl_get_false(self):
        """test get method"""
        tel_number = self.client.get("Alice")
        self.assertNotEqual(tel_number, "+49 151 23456000")

    def test_cl_getall(self):
        """test getall method"""
        tel_directory = self.client.getall()  # Returns a string of all contacts
        self.assertIn("Alice: +49 151 23456789", tel_directory)
        self.assertIn("Bob: +49 152 98765432", tel_directory)
        self.assertIn("Charlie: +49 160 11122233", tel_directory)
        self.assertIn("David: +49 171 44455566", tel_directory)
        self.assertIn("Eva: +49 172 77788899", tel_directory)
        self.assertIn("Frank: +49 173 33344455", tel_directory)
        self.assertIn("Grace: +49 174 66677788", tel_directory)
        self.assertIn("Hannah: +49 175 99900011", tel_directory)
        self.assertIn("Ivan: +49 176 55566677", tel_directory)
        self.assertIn("Julia: +49 177 88899900", tel_directory)


    def test_cl_getall_false(self):
        """test getall method"""
        tel_directory = self.client.getall()  # Returns a string of all contacts
        self.assertIn("Alice: +49 151 23456789", tel_directory)
        self.assertIn("Bob: +49 152 98765432", tel_directory)
        self.assertNotIn("Alice: +49 151 23456000", tel_directory)
        self.assertNotIn("Bob: +49 152 98765111", tel_directory)


    def test_cl_not_found(self):
        """test name not found"""
        tel_number = self.client.get("Vince")
        self.assertEqual(tel_number, "Number not found for: Vince")

    def tearDown(self):
        self.client.close()  # terminate client after each test

    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False  # break out of server loop. pylint: disable=protected-access
        cls._server_thread.join()  # wait for server thread to terminate

    



if __name__ == '__main__':
    unittest.main()
