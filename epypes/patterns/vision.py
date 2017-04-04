
from epypes.node import Node

class ImageRequest(object):
    pass

class CameraGrabNode(Node):

    def __init__(self, ImageGrabberClass, cam_id):

        self._grabber = ImageGrabberClass(cam_id)

        def grab_func(event_token=ImageRequest()):
            return self._grabber.grab_image()

        name = '{0}Node_{1}'.format(ImageGrabberClass.__name__, cam_id)
        Node.__init__(self, name, grab_func)
