from __future__ import print_function

from threading import Thread

from epypes.dag import UnderfinedSourceTokensException

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
                break

            try:
                input_kvargs = self._event_dispatcher(event)
                self._callback_pipeline.run(self._tokens_to_get, **input_kvargs)
            except UnderfinedSourceTokensException:
                pname = self._callback_pipeline.name
                msg = 'Event supplied to {} doed not correspond to the required source tokens'.format(pname)
                print(msg)
            #except Exception as err:
            #    print('An exception occured: ', err)

    def request_stop(self):
        self._q.put('STOP_REQUEST')
