import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.abspath('../RPALib'))
sys.path.append(os.path.join(os.getcwd(), 'epypes/protobuf'))

print(os.getcwd())

import numpy as np
import cv2
import pickle
import time
from functools import partial
from glob import glob
from itertools import cycle

from epypes.queue import Queue
from epypes.zeromq import ZeroMQSubscriber, ZeroMQPublisher
from epypes.loop import CommonEventLoop
from epypes.compgraph import add_new_vertices
from epypes.pipeline import FullPipeline
from epypes.protobuf.imagepair_pb2 import ImagePair
from epypes.protobuf.justbytes_pb2 import JustBytes
from epypes.protobuf.event_pb2 import Event
from epypes.protobuf.pbprocess import add_attribute, copy_downstream_attributes
from epypes.cli import parse_pubsub_args

from rpa.features import create_feature_matching_cg, METHOD_PARAMS

default_sub_address = 'ipc:///tmp/psloop-vision-request'
default_pub_address = 'ipc:///tmp/psloop-vision-response'

images1_mask = '../DATA/IMG/stereo/robotmac/left_im*.png'
images2_mask = '../DATA/IMG/stereo/robotmac/right_im*.png'

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

def get_image_cv2(pb_object, get_first):

    im_bytes = pb_object.image1.bytes if get_first else pb_object.image2.bytes

    buff_np = np.fromstring(im_bytes, dtype='uint8')
    return cv2.imdecode(buff_np, flags=cv2.IMREAD_GRAYSCALE)

def dispatch_event(e):

    pb_object = ImagePair()
    pb_object.ParseFromString(e)

    return {'pb_object': pb_object}

def prepare_output(pipe):

    t0 = time.time()

    pose = np.array([1, 1, 1])

    pb_out = JustBytes()
    pb_out.contents = pickle.dumps(pose)

    pb_imagepair = pipe['pb_object']

    copy_downstream_attributes(pb_imagepair, pb_out)
    add_attribute(pb_out, 'vision_processing_time', pipe.time)
    add_attribute(pb_out, 'cgraph_overhead', pipe.compute_overhead())
    add_attribute(pb_out, 'time_visionpipe_reacted', pipe.loop.counter.timestamp_event_arrival)
    add_attribute(pb_out, 'time_out_prep_start', t0)

    for k, v in pipe.attributes.items():
        add_attribute(pb_out, k, v)

    add_attribute(pb_out, 'time_visionpipe_pub', time.time())

    return pb_out.SerializeToString()


if __name__ == '__main__':

    pub_address, sub_address = parse_pubsub_args(default_pub_address, default_sub_address)

    q_in = Queue()
    q_images = Queue()
    q_out = Queue()

    # =============== IMACQ  =============== #

    subscriber = ZeroMQSubscriber(sub_address, q_in)

    get_stereopair = create_queue_putter(gimme_stereopair, q_images)
    loop = CommonEventLoop(q_in, get_stereopair)

    # =============== VISIONPIPE  =============== #

    CHOSEN_METHOD = 'orb'

    cg_match = create_feature_matching_cg(CHOSEN_METHOD)

    get_im_1 = partial(get_image_cv2, get_first=True)
    get_im_2 = partial(get_image_cv2, get_first=False)

    add_func_dict = {'get_image_1': get_im_1, 'get_image_2': get_im_2}
    add_func_io = {'get_image_1': ('pb_object', 'image_1'), 'get_image_2': ('pb_object', 'image_2')}

    cg_match = add_new_vertices(cg_match, add_func_dict, add_func_io)

    ft = {p: None for p in METHOD_PARAMS[CHOSEN_METHOD]}
    ft['mask_1'] = None
    ft['mask_2'] = None
    ft['normType'] = cv2.NORM_HAMMING
    ft['crossCheck'] = True

    pipe = FullPipeline('StereoMatcher', cg_match, q_images, q_out, dispatch_event, prepare_output, frozen_tokens=ft)

    publisher = ZeroMQPublisher(pub_address, q_out)

    # =============== STARTUP  =============== #

    print('Starting publisher at', pub_address)
    publisher.start()
    print('Starting FullPipeline')
    pipe.listen()
    print('Starting CommonEventLoop')
    loop.start()
    print('Starting subscriber at', sub_address)
    subscriber.start()
