from queue import Queue
from glob import glob
from itertools import cycle

from epypes.zeromq import ZeroMQSubscriber, ZeroMQPublisher
from epypes.loop import CommonEventLoop
from epypes.protobuf.imagepair_pb2 import ImagePair

default_sub_address = 'ipc:///tmp/psloop-vision-request'
default_pub_address = 'ipc:///tmp/psloop-stereopair'

images1_mask = '../DATA/IMG/calib/opencv_left/*.jpg'
images2_mask = '../DATA/IMG/calib/opencv_right/*.jpg'

images1 = (open(fname, 'rb').read() for fname in glob(images1_mask))
images2 = (open(fname, 'rb').read() for fname in glob(images2_mask))
image_pairs = zip(images1, images2)
im_cycle = cycle(image_pairs)

def gimme_stereopair():
    im1, im2 = next(im_cycle)

    pb_image_pair = ImagePair()
    pb_image_pair.image1 = im1
    pb_image_pair.image2 = im2

    return pb_image_pair.SerializeToString()

def create_queue_putter(func, q_out):

    def wrapper(event):
        q_out.put(func())

    return wrapper

if __name__ == '__main__':

    sub_address = default_sub_address
    pub_address = default_pub_address

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





