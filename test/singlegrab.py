# py27 with simplecv
from __future__ import print_function

import sys

sys.path.append('../VisionLab')
from avtgrab import AVTImageGrabber

import time

from epypes.patterns.vision import CameraGrabNode
from epypes.pipeline import Pipeline, make_pipeline

if __name__ == '__main__':

    cam = CameraGrabNode(AVTImageGrabber, 0)

    pipe, qin, qout = make_pipeline(Pipeline('GrabPipe', [cam]))
    pipe.listen()

    for i in range(1000):
        time.sleep(1)
        qin.put(i)
        while qout.empty():
            time.sleep(0.01)
        print(i, qout.qsize(), pipe.time)
        im = qout.get()
