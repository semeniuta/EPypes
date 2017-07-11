import zmq
import random
import time

address = 'ipc:///tmp/epypeszmq-testpub'

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(address)

while True:

    time.sleep(5)
    current_num = random.randint(1, 10)
    print('Sending {}'.format(current_num))
    pub_socket.send_string(str(current_num))




