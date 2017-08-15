'''
Implementation of pipeline classes and related functions
'''

from __future__ import print_function

from epypes.node import Node
from epypes.loop import EventLoop
from epypes.compgraph import CompGraph, CompGraphRunner

def run_and_put_to_q(pipeline_object, q, tokens_to_get, **kvargs):
    res = Pipeline.run(pipeline_object, tokens_to_get, **kvargs)
    q.put(res)

def attach(pipeline, nd, tokens_as_input, names_of_outputs, new_name):

    func_dict = dict(pipeline.cgraph.functions)
    func_io = dict(pipeline.cgraph.func_io)

    func_dict[nd.name] = nd
    func_io[nd.name] = tokens_as_input, names_of_outputs

    new_cg = CompGraph(func_dict, func_io)
    frozen = pipeline.runner.frozen_tokens

    new_pipeline = Pipeline(new_name, new_cg, frozen_tokens=frozen)
    return new_pipeline


class Pipeline(Node):

    def __init__(self, name, comp_graph, frozen_tokens=None):
        self._cg = comp_graph.to_cg_with_nodes()
        self._runner = CompGraphRunner(self._cg, frozen_tokens)

        def master_function(**kvargs):
            self._runner.run(**kvargs)

        super(Pipeline, self).__init__(name, master_function)

    def run(self, tokens_to_get=None, **kvargs):
        self.__call__(**kvargs)

        if tokens_to_get is not None:
            res = {tk: self._runner.token_value(tk) for tk in tokens_to_get}
            return res

    def modify_frozen_token(self, token_name, new_value):
        self._runner.freeze_token(token_name, new_value)

    def traverse_time(self):
        return (self.name, self.time, tuple(nd.traverse_time() for nd in self._cg.nodes.values()))

    def compute_overhead(self):
        _, time_total, tt_nodes = self.traverse_time()
        time_nodes = (t for _, t in tt_nodes)
        return time_total - sum(time_nodes)


    def token_value(self, token_name):
        return self._runner.token_value(token_name)

    def __getitem__(self, token_name):
        return self.token_value(token_name)

    def stop(self):
        for node in self._cg.nodes.values():
            node.stop()

    @property
    def cgraph(self):
        return self._cg

    @property
    def runner(self):
        return self._runner

class SourcePipeline(Pipeline):

    def __init__(self, name, comp_graph, q_out, frozen_tokens=None):
        self._qout = q_out
        super(SourcePipeline, self).__init__(name, comp_graph, frozen_tokens)

    def run(self, tokens_to_get=None, **kvargs):
        run_and_put_to_q(self, self._qout, tokens_to_get, **kvargs)

class SinkPipeline(Pipeline):

    def __init__(self, name, comp_graph, q_in, event_dispatcher=None, frozen_tokens=None):

        self._qin = q_in

        def basic_event_dispatcher(e):
            return e

        if event_dispatcher is None:
            event_dispatcher = basic_event_dispatcher

        self._loop = EventLoop(q_in, self, event_dispatcher)
        super(SinkPipeline, self).__init__(name, comp_graph, frozen_tokens)

    def listen(self):
        self._loop.start()

    def stop(self):
        self._loop.stop()
        self._loop.join()
        Pipeline.stop(self)

class FullPipeline(SinkPipeline):

    def __init__(self, name, comp_graph, q_in, q_out, event_dispatcher=None, frozen_tokens=None):
        self._qout = q_out
        super(FullPipeline, self).__init__(name, comp_graph, q_in, event_dispatcher, frozen_tokens)

    def run(self, tokens_to_get=None, **kvargs):
        run_and_put_to_q(self, self._qout, tokens_to_get, **kvargs)

