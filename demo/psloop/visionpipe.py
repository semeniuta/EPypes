import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'epypes/protobuf'))

import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import pickle
import time

from epypes.queue import Queue
from epypes.compgraph import CompGraph
from epypes.pipeline import FullPipeline
from epypes.zeromq import ZeroMQSubscriber, ZeroMQPublisher
from epypes.protobuf.imagepair_pb2 import ImagePair
from epypes.protobuf.justbytes_pb2 import JustBytes
from epypes.protobuf.pbprocess import copy_downstream_attributes, add_attribute
from epypes.cli import parse_pubsub_args

def get_image_from_pb(pb_object):

    return pb_object.image1.bytes

def open_image_from_bytes(image_bytes):

    buff = BytesIO(image_bytes)
    im = np.array(Image.open(buff))
    return im

def find_cbc(img, pattern_size_wh, searchwin_size=5, findcbc_flags=None):

    if findcbc_flags == None:
        res = cv2.findChessboardCorners(img, pattern_size_wh)
    else:
        res = cv2.findChessboardCorners(img, pattern_size_wh, flags=findcbc_flags)

    found, corners = res

    if found:
        term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
        cv2.cornerSubPix(img, corners, (searchwin_size, searchwin_size), (-1, -1), term)

    return res

def cbc_opencv_to_numpy(success, cbc_res):

    if success:
        return cbc_res.reshape(-1, 2)
    else:
        return None

def ndarray_to_bytes(a):
    pb_object = JustBytes()
    pb_object.contents = pickle.dumps(a)
    return pb_object

class CGFindCorners(CompGraph):

    def __init__(self):
        func_dict = {
            'get_image_from_pb': get_image_from_pb,
            'open_image': open_image_from_bytes,
            'find_corners': find_cbc,
            'reformat_corners': cbc_opencv_to_numpy,
            'ndarray_to_bytes': ndarray_to_bytes
        }

        func_io = {
            'get_image_from_pb': ('pb_object', 'image_bytes'),
            'open_image': ('image_bytes', 'image'),
            'find_corners': (('image', 'pattern_size_wh'), ('success', 'corners_opencv')),
            'reformat_corners': (('success', 'corners_opencv'), 'corners_np'),
            'ndarray_to_bytes': ('corners_np', 'corners_np_bytes')
        }

        super(CGFindCorners, self).__init__(func_dict, func_io)

def dispatch_event(e):

    pb_object = ImagePair()
    pb_object.ParseFromString(e)

    return {'pb_object': pb_object}

def prepare_output(pipe):

    arr = pipe['corners_np']

    pb_out = JustBytes()
    pb_out.contents = pickle.dumps(arr)

    pb_imagepair = pipe['pb_object']

    copy_downstream_attributes(pb_imagepair, pb_out)
    add_attribute(pb_out, 'vision_processing_time', pipe.time)
    add_attribute(pb_out, 'epypes_overhead', pipe.compute_overhead())
    add_attribute(pb_out, 'time_visionpipe_pub', time.time())
    add_attribute(pb_out, 'time_visionpipe_reacted', pipe.loop.counter.timestamp_event_arrival)

    return pb_out.SerializeToString()

default_sub_address = 'ipc:///tmp/psloop-stereopair'
default_pub_address = 'ipc:///tmp/psloop-vision-response'

if __name__ == '__main__':

    pub_address, sub_address = parse_pubsub_args(default_pub_address, default_sub_address)

    q_in = Queue()
    q_out = Queue()

    subscriber = ZeroMQSubscriber(sub_address, q_in)

    cg = CGFindCorners()
    pipe = FullPipeline('FindCorners', cg, q_in, q_out, dispatch_event, prepare_output)
    pipe['pattern_size_wh'] = (9, 6)

    publisher = ZeroMQPublisher(pub_address, q_out)

    print('Starting publisher at', pub_address)
    publisher.start()
    print('Starting FullPipeline')
    pipe.listen()
    print('Starting subscriber at', sub_address)
    subscriber.start()



