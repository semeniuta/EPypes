import os
import sys
import time
import uuid

sys.path.append(os.getcwd())

from epypes.zeromq import ZeroMQPublisher
from epypes.queue import Queue

default_address = 'ipc:///tmp/epypeszmq-pub'

if len(sys.argv) == 1:
    address = default_address
else:
    address = sys.argv[1]

q = Queue()
publisher = ZeroMQPublisher(address, q)
publisher.start()

print('Publishing at', address)

for i in range(10):
    time.sleep(0.5)
    msg = str(uuid.uuid4())[:8].encode()
    q.put(msg)
    print('Sent: ', msg)

publisher.stop()
print('Stopped', publisher)





