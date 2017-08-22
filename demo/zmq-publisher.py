import sys
import zmq
import random
import time

default_address = 'ipc:///tmp/epypeszmq-pub_1'

if len(sys.argv) == 1:
    address = default_address
else:
    address = sys.argv[1]

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(address)

print('Publishing at ', address)

while True:

    current_num = random.randint(1, 10)
    print('Sending {}'.format(current_num))
    pub_socket.send_string(str(current_num))
    time.sleep(0.5)




