from __future__ import print_function

import time

from epypes.commons import GenericObject
from epypes import exceptions

class Node(GenericObject):

    def __init__(self, name, func, **kvargs):
        GenericObject.__init__(self, name)
        self._func = func
        self._kvargs = kvargs
        self._run_count = 0
        self._time = None
        self._exception = None
        self._state = 'ready'

    def modify_argument(self, key, new_value):

        if key not in self._kvargs:
            raise exceptions.IncorrectArgKeyException()

        self._kvargs[key] = new_value

    def run(self, token=None):

        if self.state is not 'ready':
            raise exceptions.NodeCannotBeRunException()

        self._state = 'running'

        try:
            t0 = time.time()
            res = self._call_main_func(token)
            t1 = time.time()
            self._time = t1 - t0
            self._run_count += 1
        except Exception as e:
            self._exception = (self.name, e)
            self._time = None
            res = e
            self._state = 'exception'

        self._state = 'ready'
        return res

    def _call_main_func(self, token=None):
        if token is None:
            res = self._func(**self._kvargs)
        else:
            res = self._func(token, **self._kvargs)
        return res

    @property
    def state(self):
        return self._state

    @property
    def time(self):
        if self._time is None:
            raise exceptions.TimeRequestBeforeRunException()
        return self._time

    @property
    def run_count(self):
        return self._run_count

    def traverse_time(self):
        return (self.name, self.time)

    def request_stop(self):
        self._state = 'stopped'

    def get_arguments(self):
        return self._kvargs
