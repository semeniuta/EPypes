import sys
import zmq
import time
import itertools
from glob import glob

import imagepair_pb2

default_address = 'ipc:///tmp/epypeszmq-cbim'
images1_mask = '../DATA/IMG/calib/opencv_left/*.jpg'
images2_mask = '../DATA/IMG/calib/opencv_right/*.jpg'

if len(sys.argv) == 1:
    address = default_address
else:
    address = sys.argv[1]

images1 = (open(fname, 'rb').read() for fname in glob(images1_mask))
images2 = (open(fname, 'rb').read() for fname in glob(images2_mask))
image_pairs = zip(images1, images2)

im_cycle = itertools.cycle(image_pairs)

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(address)

print('Publishing images at ', address)

#for im1, im2 in im_cycle:
for im1, im2 in image_pairs:

    time.sleep(0.003) # if this is commented and iteration is over im_cycle, the subscriber doesn't get anything

    pb_image_pair = imagepair_pb2.ImagePair()
    pb_image_pair.image1 = im1
    pb_image_pair.image2 = im2

    pub_socket.send(pb_image_pair.SerializeToString()) # bytes object
    print('sent')
