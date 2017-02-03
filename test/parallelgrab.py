from datetime import datetime

from epypes.patterns.parallel import create_ppnode_from_nodes
from epypes.splitters import copy_input_splitter
from epypes.patterns.vision import CameraGrabNode
from epypes.pipeline import SimplePipeline, SinkPipeline, make_pipeline
from epypes.node import Node

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
    sg = create_ppnode_from_nodes('MyStereoGrabber', [cam1, cam2], copy_input_splitter)

    spipe = SimplePipeline('StereoGrabPipe', [sg])
    pipe, qin, qout = make_pipeline(spipe)

    print_node = Node('Printer', lambda x: print(x, abs(x[0][1] - x[1][1])))
    pipe_out = SinkPipeline('PrinterPipe', [print_node], qout)

    pipe.listen()
    pipe_out.listen()
