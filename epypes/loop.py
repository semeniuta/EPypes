from __future__ import print_function

from threading import Thread
import traceback
import time

from epypes.compgraph import UndefinedSourceTokensException
from epypes.util import generate_short_uuid


class CommonEventLoop(Thread):

    def __init__(self, q, callback_func):

        self._q = q
        self._callback_func = callback_func
        self._stop_const = generate_short_uuid()

        super(CommonEventLoop, self).__init__(target=self._eventloop)

    def _eventloop(self):

        while True:

            event = self._q.get()

            if event == self._stop_const:
                print('Stopping {}'.format(self))
                break

            try:
                self._callback_func(event)
            except Exception:
                print('An exception occurred when invoking {}. Exception details:'.format(self._callback_func))
                traceback.print_exc()

    def stop(self):
        self._q.put(self._stop_const)


class EventLoop(Thread):

    def __init__(self, q, callback_pipeline, event_dispatcher):

        self._q = q
        self._callback_pipeline = callback_pipeline
        self._event_dispatcher = event_dispatcher
        self._stop_const = generate_short_uuid()

        Thread.__init__(self, target=self._eventloop)

    def _eventloop(self):

        while True:

            event = self._q.get()

            if event == self._stop_const:
                print('Stopping {}'.format(self))
                break

            try:

                self._callback_pipeline.attributes['time_dispatch_0'] = time.perf_counter()
                input_kwargs = self._event_dispatcher(event)
                self._callback_pipeline.attributes['time_dispatch_1'] = time.perf_counter()
                self._callback_pipeline.run(**input_kwargs)

            except UndefinedSourceTokensException:
                pname = self._callback_pipeline.name
                msg = 'Event supplied to {} does not correspond to the required source tokens'.format(pname)
                print(msg)
            except Exception:
                print('An exception occurred when invoking {}. Exception details:'.format(self._callback_pipeline))
                traceback.print_exc()

    def stop(self):
        self._q.put(self._stop_const)
