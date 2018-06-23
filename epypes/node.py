from __future__ import print_function

import time

from epypes.commons import GenericObject

class Node(GenericObject):

    def __init__(self, name, func):
        GenericObject.__init__(self, name)
        self._func = func
        self._run_count = 0
        self._time = 0

    def __call__(self, *args, **kwargs):
        '''
        NodeBasedCompGraph calls a node using exclusively *args (positional arguments)
        **kwargs are used by Pipeline.run (Pipeline is a subclass of Node)
        for forwarding keys/values of free source tokens
        '''

        t0 = time.time()
        res = self._func(*args, **kwargs)
        t1 = time.time()
        self._time = t1 - t0
        self._run_count += 1
        return res

    @property
    def time(self):
        return self._time

    @property
    def run_count(self):
        return self._run_count

    def traverse_time(self):
        return self.name, self.time

    def stop(self):
        pass
