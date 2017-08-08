import sys
import numpy as np
from queue import Queue
import cv2
from PIL import Image
from io import BytesIO

from epypes.compgraph import CompGraph
from epypes.pipeline import SinkPipeline
from epypes.zeromq import ZeroMQSubscriber

def open_image_from_bytesarray(ba):

    buff = BytesIO(ba)
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

class CGFindCorners(CompGraph):

    def __init__(self):
        func_dict = {
            'open_image': open_image_from_bytesarray,
            'find_corners': find_cbc,
            'reformat_corners': cbc_opencv_to_numpy
        }

        func_io = {
            'open_image': ('bytes', 'image'),
            'find_corners': (('image', 'pattern_size_wh'), ('success', 'corners_opencv')),
            'reformat_corners': (('success', 'corners_opencv'), 'corners_np')
        }

        super(CGFindCorners, self).__init__(func_dict, func_io)


if __name__ == '__main__':

    def dispatch_event(e):
        return {'bytes': e}

    default_address = 'ipc:///tmp/epypeszmq-cbim'

    if len(sys.argv) == 1:
        address = default_address
    else:
        address = sys.argv[1]

    q = Queue()
    cg = CGFindCorners()
    pipe = SinkPipeline('FindCorners', cg, q, event_dispatcher=dispatch_event)
    pipe.runner.token_manager.freeze_token('pattern_size_wh', (9, 6))
    sub = ZeroMQSubscriber(address, q)

    def stop():
        sub.stop()
        pipe.stop()

    pipe.listen()
    sub.start()
