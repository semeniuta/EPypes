from __future__ import print_function

from epypes.commons import GenericObject

import threading
import sys
ver = sys.version_info[:2]
if ver[0] == 2:
    import Queue as queue
else:
    import queue

def basic_eventloop(callback_node, token_q, stop_q):
    while True:
        if not stop_q.empty():
            stop_q.get()
            break

        if not token_q.empty():
            token = token_q.get()
            callback_node.run(token)

class EventLoop(GenericObject):

    def __init__(self, q, callback_node):
        name = 'In{}'.format(callback_node.__class__.__name__)
        GenericObject.__init__(self, name)

        self._callback_node = callback_node
        self._token_q = q
        self._stop_q = queue.Queue()

        t_args = (self._callback_node, self._token_q, self._stop_q)
        self._thread = threading.Thread(target=basic_eventloop, args=t_args)

    def start(self):
        self._thread.start()

    def request_stop(self):
        self._stop_q.put(None)
        self._thread.join()