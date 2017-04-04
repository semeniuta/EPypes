from datetime import datetime

#from epypes.patterns.parallel import create_ppnode_from_nodes
#from epypes.payload import copy_input_splitter
from epypes.patterns.vision import CameraGrabNode
#from epypes.pipeline import Pipeline, SinkPipeline
#from epypes.node import Node

if __name__ == '__main__':

    import time
    import random
    import skimage.data

    class DummyCam(object):
        def __init__(self, id):
            self.id = id

        def grab_image(self):

            delay = random.random()
            time.sleep(delay)

            return skimage.data.coffee()


    cam1 = CameraGrabNode(DummyCam, 0)
    cam2 = CameraGrabNode(DummyCam, 1)

    #sg = create_ppnode_from_nodes('MyStereoGrabber', [cam1, cam2], copy_input_splitter)

    #spipe = Pipeline('StereoGrabPipe', [sg])
    #pipe, qin, qout = make_full_pipeline(spipe)

    #print_node = Node('Printer', lambda x: print(x, abs(x[0][1] - x[1][1])))
    #pipe_out = SinkPipeline('PrinterPipe', [print_node], qout)

    #pipe.listen()
    #pipe_out.listen()
