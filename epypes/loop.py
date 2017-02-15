from __future__ import print_function

from threading import Thread
import sys
ver = sys.version_info[:2]
if ver[0] == 2:
    import Queue as queue
else:
    import queue

class EventLoop(Thread):

    def __init__(self, q, callback_node):

        self._callback_node = callback_node
        self._token_q = q
        self._stop_q = queue.Queue()

        Thread.__init__(self, target=self._eventloop)

    def _eventloop(self):

        while True:

            if not self._stop_q.empty():
                self._stop_q.get()
                break

            if not self._token_q.empty():
                token = self._token_q.get()
                self._callback_node.run(token)

    def request_stop(self):
        self._stop_q.put(None)