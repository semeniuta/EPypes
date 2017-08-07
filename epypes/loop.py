from __future__ import print_function

from threading import Thread
import traceback

from epypes.compgraph import UnderfinedSourceTokensException

class CommonEventLoop(Thread):

    def __init__(self, q, callback_func):

        self._q = q
        self._callback_func = callback_func

        Thread.__init__(self, target=self._eventloop)

    def _eventloop(self):

        while True:

            event = self._q.get()

            if event == 'STOP_REQUEST':
                print('Stopping {}'.format(self))
                break

            try:
                self._callback_func(event)
            except Exception:
                print('An exception occurred when invoking {}. Exception details:'.format(self._callback_func))
                traceback.print_exc()

    def stop(self):
        self._q.put('STOP_REQUEST')

class EventLoop(Thread):

    def __init__(self, q, callback_pipeline, event_dispatcher, tokens_to_get=None):

        self._q = q
        self._callback_pipeline = callback_pipeline
        self._event_dispatcher = event_dispatcher

        self._tokens_to_get = tokens_to_get

        Thread.__init__(self, target=self._eventloop)

    def _eventloop(self):

        while True:

            event = self._q.get()

            if event == 'STOP_REQUEST':
                print('Stopping {}'.format(self))
                break

            try:
                input_kvargs = self._event_dispatcher(event)
                self._callback_pipeline.run(self._tokens_to_get, **input_kvargs)
            except UnderfinedSourceTokensException:
                pname = self._callback_pipeline.name
                msg = 'Event supplied to {} does not correspond to the required source tokens'.format(pname)
                print(msg)
            except Exception:
                print('An exception occurred when invoking {}. Exception details:'.format(self._callback_pipeline))
                traceback.print_exc()

    def stop(self):
        self._q.put('STOP_REQUEST')
