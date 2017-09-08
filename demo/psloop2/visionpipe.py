import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.abspath('../RPALib'))
sys.path.append(os.path.join(os.getcwd(), 'epypes/protobuf'))

import numpy as np
import cv2
import pickle
import time
from functools import partial

from epypes.queue import Queue
from epypes.compgraph import CompGraph, add_new_vertices
from epypes.pipeline import FullPipeline
from epypes.zeromq import ZeroMQSubscriber, ZeroMQPublisher
from epypes.protobuf.imagepair_pb2 import ImagePair
from epypes.protobuf.justbytes_pb2 import JustBytes
from epypes.protobuf.pbprocess import copy_downstream_attributes, add_attribute
from epypes.cli import parse_pubsub_args

from rpa.features import create_feature_matching_cg, METHOD_PARAMS

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
    add_attribute(pb_out, 'epypes_overhead', pipe.compute_overhead())
    add_attribute(pb_out, 'time_visionpipe_reacted', pipe.loop.counter.timestamp_event_arrival)
    add_attribute(pb_out, 'time_out_prep_start', t0)

    for k, v in pipe.attributes.items():
        add_attribute(pb_out, k, v)

    add_attribute(pb_out, 'time_visionpipe_pub', time.time())

    return pb_out.SerializeToString()


default_sub_address = 'ipc:///tmp/psloop-stereopair'
default_pub_address = 'ipc:///tmp/psloop-vision-response'

if __name__ == '__main__':

    pub_address, sub_address = parse_pubsub_args(default_pub_address, default_sub_address)

    q_in = Queue()
    q_out = Queue()

    subscriber = ZeroMQSubscriber(sub_address, q_in)

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

    pipe = FullPipeline('StereoMatcher', cg_match, q_in, q_out, dispatch_event, prepare_output, frozen_tokens=ft)

    publisher = ZeroMQPublisher(pub_address, q_out)

    print('Starting publisher at', pub_address)
    publisher.start()
    print('Starting FullPipeline')
    pipe.listen()
    print('Starting subscriber at', sub_address)
    subscriber.start()
