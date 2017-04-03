'''
Implementation of pipeline classes and related functions
'''

from __future__ import print_function

from epypes.node import Node
from epypes.loop import EventLoop
from epypes.dag import CompGraphRunner

def run_and_put_to_q(pipeline_object, q, tokens_to_get, **kvargs):
    res = Pipeline.run(pipeline_object, tokens_to_get, **kvargs)
    q.put(res)

def is_exception(token):
    return issubclass(type(token), Exception)

class Pipeline(Node):

    def __init__(self, name, comp_graph, frozen_tokens=None):
        self._cg = comp_graph.to_cg_with_nodes()
        self._runner = CompGraphRunner(self._cg, frozen_tokens)

        def master_function(**kvargs):
            self._runner.run(**kvargs)

        Node.__init__(self, name, master_function)

    def run(self, tokens_to_get=None, **kvargs):
        self.__call__(**kvargs)

        if tokens_to_get is not None:
            res = {tk: self._runner.token_value(tk) for tk in tokens_to_get}
            return res

    def modify_frozen_token(self, token_name, new_value):
        self._runner.freeze_token(token_name, new_value)

    def traverse_time(self):
        return (self.name, self.time, tuple(nd.traverse_time() for nd in self._cg.nodes))

    def token_value(self, token_name):
        return self._runner.token_value(token_name)

    def request_stop(self):
        for node in self._cg.nodes.values():
            node.request_stop()

    @property
    def graph(self):
        return self._cg

    @property
    def runner(self):
        return self._runner

class SourcePipeline(Pipeline):
    def __init__(self, name, comp_graph, q_out, frozen_tokens=None):
        self._qout = q_out
        Pipeline.__init__(self, name, comp_graph, frozen_tokens)

    def run(self, tokens_to_get=None, **kvargs):
        run_and_put_to_q(self, self._qout, tokens_to_get, **kvargs)

class SinkPipeline(Pipeline):
    def __init__(self, name, comp_graph, q_in, event_dispatcher, frozen_tokens=None):
        self._qin = q_in
        self._loop = EventLoop(q_in, self, event_dispatcher)
        Pipeline.__init__(self, name, comp_graph, frozen_tokens)

    def listen(self):
        self._loop.start()

    def request_stop(self):
        self._loop.request_stop()
        self._loop.join()
        Pipeline.request_stop(self)

class FullPipeline(SinkPipeline):
    def __init__(self, name, comp_graph, q_in, q_out, event_dispatcher, tokens_to_get, frozen_tokens=None):
        self._qin = q_in
        self._qout = q_out
        self._loop = EventLoop(q_in, self, event_dispatcher, tokens_to_get)
        Pipeline.__init__(self, name, comp_graph, frozen_tokens)

    def run(self, tokens_to_get=None, **kvargs):
        run_and_put_to_q(self, self._qout, tokens_to_get, **kvargs)

