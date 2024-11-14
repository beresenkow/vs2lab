from time import sleep
import rpc
import logging
from context import lab_logging

def callback(result_list):
    print("Result: {}".format(result_list.value))
    

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list, callback)

#doing funny stuff while waiting
for i in range(5) :
    print("client am Clientieren")
    sleep(2)

cl.stop()
