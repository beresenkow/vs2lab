from time import sleep
import rpc
import logging
from context import lab_logging

def callback(result_list):
    print("Result: {}".format(result_list.value))
    cl.stop()

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list, callback)

#do some random stuff here while waiting
for i in range(7):
    print("I'm  the client and I am doing other things while waiting!!")
    sleep(2)