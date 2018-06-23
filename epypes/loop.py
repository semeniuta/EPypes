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

        self._counter = TimeCounter(q)

        Thread.__init__(self, target=self._eventloop)

    def _eventloop(self):

        while True:

            event = self._q.get()
            self._counter.on_event_arrival()

            if event == self._stop_const:
                print('Stopping {}'.format(self))
                break

            try:

                self._callback_pipeline.attributes['time_dispatch_0'] = time.perf_counter()
                input_kwargs = self._event_dispatcher(event)
                self._callback_pipeline.attributes['time_dispatch_1'] = time.perf_counter()

                self._counter.on_processing_start()
                self._callback_pipeline.run(**input_kwargs)
                self._counter.on_processing_end()
                #print(self._counter.summary)

            except UndefinedSourceTokensException:
                pname = self._callback_pipeline.name
                msg = 'Event supplied to {} does not correspond to the required source tokens'.format(pname)
                print(msg)
            except Exception:
                print('An exception occurred when invoking {}. Exception details:'.format(self._callback_pipeline))
                traceback.print_exc()

    def stop(self):
        self._q.put(self._stop_const)

    @property
    def counter(self):
        return self._counter


class TimeCounter(object):

    def __init__(self, q):

        self._q = q

        self._t_prev_event = None
        self._t_event = None

        self._t_process_start = None
        self._t_process_end = None

        self._qsize = None

        self._summary = None

    def on_event_arrival(self):
        t = time.perf_counter()
        self._t_prev_event = self._t_event
        self._t_event = t
        self._qsize = self._q.qsize()

    def on_processing_start(self):
        self._t_process_start = time.perf_counter()

    def on_processing_end(self):
        self._t_process_end = time.perf_counter()
        self._summary = self._prepare_summary()

    def _prepare_summary(self):

        summary = {
            'time_processing': self._t_process_end - self._t_process_start,
            'qsize': self._qsize
        }

        if self._t_prev_event is None: # first time
            summary['time_interarrival'] = None
        else:
            summary['time_interarrival'] = self._t_event - self._t_prev_event

        return summary

    @property
    def summary(self):
        return self._summary

    @property
    def timestamp_event_arrival(self):
        return self._t_event






