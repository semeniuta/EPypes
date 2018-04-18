
import zmq
from threading import Thread
from epypes.loop import CommonEventLoop

class ZeroMQSubscriber(Thread):

    def __init__(self, server_address, q, sub_prefix=''):

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.SUB)
        self._socket.connect(server_address)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, sub_prefix)

        self._q = q

        self._addr = server_address
        self._stop_flag = False

        super(ZeroMQSubscriber, self).__init__(target=self._listen)

    def _listen(self):

        poller = zmq.Poller()
        poller.register(self._socket)

        while True:

            p_socks = dict(poller.poll(timeout=0))

            if self._socket in p_socks:
                msg = self._socket.recv()
                self._q.put(msg)

            if self._stop_flag is True:
                print('Stopping {}'.format(self))
                break

    def stop(self):

        self._stop_flag = True

    def __repr__(self):

        class_name = self.__class__.__name__
        return '{0}[{1}]'.format(class_name, self._addr)


class ZeroMQPublisher(CommonEventLoop):

    def __init__(self, server_address, q):

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind(server_address)

        self._addr = server_address

        super(ZeroMQPublisher, self).__init__(q, callback_func=self._send)

    def _send(self, data):

        if type(data) == str:
            self._socket.send_string(data)
        else:
            self._socket.send(data)

    def __repr__(self):

        class_name = self.__class__.__name__
        return '{0}[{1}]'.format(class_name, self._addr)

