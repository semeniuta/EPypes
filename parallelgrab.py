

import multiprocessing as mp
from multiprocessing import Queue
from datetime import datetime
import math

from epypes.pipeline import Node, SimplePipeline, SourcePipeline, SinkPipeline, Pipeline, make_pipeline
from epypes.patterns import ParallelPipesNode
from epypes.vision import CameraGrabNode

if __name__ == '__main__':

    import time
    import random

    class DummyCam(object):
        def __init__(self, id):
            self.id = id

        def grab_image(self):
            t0 = datetime.now()
            time.sleep(1 + random.random())
            t1 = datetime.now()
            span = t1 - t0
            print('It took ', span)
            return t1


    cam1 = CameraGrabNode(DummyCam, 0)
    cam2 = CameraGrabNode(DummyCam, 1)
    sg = ParallelPipesNode('MyStereoGrabber', [cam1, cam2])

    spipe = SimplePipeline('StereoGrabPipe', [sg])
    pipe, qin, qout = make_pipeline(spipe)

    print_node = Node('Printer', lambda x: print(x, abs(x[0][1] - x[1][1])))
    pipe_out = SinkPipeline('PrinterPipe', [print_node], qout)

    pipe.listen()
    pipe_out.listen()
