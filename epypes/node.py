from __future__ import print_function

import time
from epypes.commons import GenericObject

class Node(GenericObject):

    def __init__(self, name, func, **kvargs):
        GenericObject.__init__(self, name)
        self._func = func
        self._kvargs = kvargs
        self._time = None
        self._exception = None

    def modify_argument(self, key, new_value):

        if key not in self._kvargs:
            raise Exception('Incorrect argument key')

        self._kvargs[key] = new_value

    def run(self, token=None):

        try:
            t0 = time.time()
            res = self._call_main_func(token)
            t1 = time.time()
            self._time = t1 - t0
        except Exception as e:
            self._exception = (self.name, e)
            self._time = None
            res = e

        return res

    def _call_main_func(self, token=None):
        if token is None:
            res = self._func(**self._kvargs)
        else:
            res = self._func(token, **self._kvargs)
        return res

    @property
    def time(self):
        if self._time is None:
            msg = '{} has not yet ran, but time requested'.format(self.name)
            raise Exception(msg)
        return self._time

    def traverse_time(self):
        return (self.name, self.time)

    def request_stop(self):
        pass

    def get_arguments(self):
        return self._kvargs
