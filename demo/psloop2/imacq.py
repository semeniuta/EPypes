import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'epypes/protobuf'))

import time
from glob import glob
from itertools import cycle

from epypes.queue import Queue
from epypes.zeromq import ZeroMQSubscriber, ZeroMQPublisher
from epypes.loop import CommonEventLoop
from epypes.protobuf.imagepair_pb2 import ImagePair
from epypes.protobuf.event_pb2 import Event
from epypes.protobuf.pbprocess import add_attribute, copy_downstream_attributes
from epypes.cli import parse_pubsub_args

default_sub_address = 'ipc:///tmp/psloop-vision-request'
default_pub_address = 'ipc:///tmp/psloop-stereopair'

images1_mask = '../DATA/IMG/stereo/vintage/im0.png'
images2_mask = '../DATA/IMG/stereo/vintage/im1.png'

images1 = [open(fname, 'rb').read() for fname in glob(images1_mask)]
images2 = [open(fname, 'rb').read() for fname in glob(images2_mask)]
image_pairs = zip(images1, images2)
im_cycle = cycle(image_pairs)

def gimme_stereopair(event):

    time_imacq_reacted_to_request = time.time()

    event_pb = Event()
    event_pb.ParseFromString(event)

    im1, im2 = next(im_cycle)
    time_got_images = time.time()

    pb_image_pair = ImagePair()
    pb_image_pair.image1.bytes = im1
    pb_image_pair.image2.bytes = im2
    copy_downstream_attributes(event_pb, pb_image_pair)
    add_attribute(pb_image_pair, 'time_got_images', time_got_images)
    add_attribute(pb_image_pair, 'time_imacq_reacted_to_request', time_imacq_reacted_to_request)

    return pb_image_pair.SerializeToString()

def create_queue_putter(func, q_out):

    def wrapper(event):
        q_out.put(func(event))

    return wrapper

if __name__ == '__main__':

    pub_address, sub_address = parse_pubsub_args(default_pub_address, default_sub_address)

    q_in = Queue()
    q_out = Queue()

    subscriber = ZeroMQSubscriber(sub_address, q_in)

    get_stereopair = create_queue_putter(gimme_stereopair, q_out)
    loop = CommonEventLoop(q_in, get_stereopair)

    publisher = ZeroMQPublisher(pub_address, q_out)

    print('Starting publisher at', pub_address)
    publisher.start()
    print('Starting CommonEventLoop')
    loop.start()
    print('Starting subscriber at', sub_address)
    subscriber.start()





