from epypes.queue import Queue


def create_queues():

    q_in = Queue()
    q_images = Queue()
    q_out = Queue()

    return q_in, q_images, q_out


def dispatch_images(images):

    n = len(images)

    if n == 1:
        return {'image': images[0]}

    return {'image_{:d}'.format(i+1) : images[i] for i in range(n)}


class ReactiveVisionSystem(object):

    def __init__(self, subscriber, grabber, pipeline, publisher):

        self._subscriber = subscriber
        self._grabber = grabber
        self._pipeline = pipeline
        self._publisher = publisher


    def start(self, verbose=False):

        if verbose:
            print('Starting', self._publisher)
        self._publisher.start()

        if verbose:
            print('Starting', self._pipeline)
        self._pipeline.listen()

        if verbose:
            print('Starting', self._grabber)
        self._grabber.start(show_video=False)

        if verbose:
            print('Starting', self._subscriber)
        self._subscriber.start()


    def stop(self, verbose=False):

        if verbose:
            print('Stopping', self._subscriber)
        self._subscriber.stop()

        if verbose:
            print('Stopping', self._grabber)
        self._grabber.stop()

        if verbose:
            print('Stopping', self._pipeline)
        self._pipeline.stop()

        if verbose:
            print('Stopping', self._publisher)
        self._publisher.stop()
