import sys
import zmq
import time
import itertools
from glob import glob

default_address = 'ipc:///tmp/epypeszmq-cbim'
images_mask = '../DATA/IMG/calib/opencv_left/*.jpg'

if len(sys.argv) == 1:
    address = default_address
else:
    address = sys.argv[1]

images = (open(fname, 'rb').read() for fname in glob(images_mask))
im_cycle = itertools.cycle(images)

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(address)

print('Publishing images at ', address)

for im in im_cycle:

    #time.sleep(5)
    pub_socket.send(bytearray(im))
