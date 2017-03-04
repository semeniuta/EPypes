from __future__ import print_function

from threading import Thread

class StopRequest(object):
    def __repr__(self):
        return 'StopRequest'

class EventLoop(Thread):

    def __init__(self, q, callback_node):

        self._callback_node = callback_node
        self._token_q = q

        Thread.__init__(self, target=self._eventloop)

    def _eventloop(self):

        while True:

            token = self._token_q.get()

            if token == 'STOP_REQUEST':
                break

            self._callback_node.run(token)


    def request_stop(self):
        self._token_q.put('STOP_REQUEST')
