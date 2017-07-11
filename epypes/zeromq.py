
import zmq
from threading import Thread

class ZeroMQSubscriber(Thread):

    def __init__(self, server_address, q, sub_prefix=''):

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.SUB)

        self._socket.connect(server_address)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, sub_prefix)

        self._q = q

        self._stop_flag = False

        super(ZeroMQSubscriber, self).__init__(target=self._listen)

    def _listen(self):

        while True:

            try:
                msg = self._socket.recv_string(flags=zmq.NOBLOCK)
                self._q.put(msg)
            except zmq.error.Again:
                if self._stop_flag is True:
                    print('Stopping {}'.format(self))
                    break

    def stop(self):

        self._stop_flag = True













