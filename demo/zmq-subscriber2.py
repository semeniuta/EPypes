import os
import sys
import time

sys.path.append(os.getcwd())

from epypes.loop import CommonEventLoop
from epypes.zeromq import ZeroMQSubscriber
from epypes.queue import Queue

default_address = 'ipc:///tmp/epypeszmq-pub'

if len(sys.argv) == 1:
    address = default_address
else:
    address = sys.argv[1]

q = Queue()

qhandler = CommonEventLoop(
    q,
    lambda x: print('Received', x)
)
qhandler.start()

print('Listening to', address)
subscriber = ZeroMQSubscriber(address, q)
subscriber.start()

print('waiting for 10 seconds before stopping')
time.sleep(10)

subscriber.stop()
qhandler.stop()




