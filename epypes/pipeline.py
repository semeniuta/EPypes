'''
Implementation of pipeline classes and related functions
'''

from __future__ import print_function

from epypes.node import Node
from epypes.loop import EventLoop
from epypes.compgraph import CompGraph, CompGraphRunner

import time


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

        self._attributes = dict()

        super(Pipeline, self).__init__(name, func=self._runner.run)

    def run(self, **kwargs):
        self.__call__(**kwargs)

    def modify_frozen_token(self, token_name, new_value):
        self._runner.freeze_token(token_name, new_value)

    def traverse_time(self):
        return self.name, self.time, tuple(nd.traverse_time() for nd in self._cg.nodes.values())

    def compute_overhead(self):
        _, time_total, tt_nodes = self.traverse_time()
        time_nodes = (t for _, t in tt_nodes)
        return time_total - sum(time_nodes)

    def __getitem__(self, token_name):
        return self._runner[token_name]

    def token_value(self, token_name): # deprecated
        return self[token_name]

    def __setitem__(self, token_name, frozen_value):
        self.modify_frozen_token(token_name, frozen_value)

    def stop(self):
        for node in self._cg.nodes.values():
            node.stop()

    def set_attr(self, k, v):
        self._attributes[k] = v

    def get_attr(self, k):

        if k in self._attributes:
            return self._attributes[k]

        return None

    @property
    def attributes(self):
        return self._attributes

    @property
    def cgraph(self):
        return self._cg

    @property
    def runner(self):
        return self._runner


class SinkPipeline(Pipeline):

    def __init__(self, name, comp_graph, q_in, event_dispatcher, frozen_tokens=None):

        self._qin = q_in

        self._loop = EventLoop(q_in, self, event_dispatcher)
        super(SinkPipeline, self).__init__(name, comp_graph, frozen_tokens)

    def listen(self):
        self._loop.start()

    def stop(self):
        self._loop.stop()
        self._loop.join()
        Pipeline.stop(self)

    @property
    def loop(self):
        return self._loop


class SourcePipeline(Pipeline):

    def __init__(self, name, comp_graph, q_out, out_prep_func, frozen_tokens=None):

        self._qout = q_out
        self._out_prep_func = out_prep_func
        super(SourcePipeline, self).__init__(name, comp_graph, frozen_tokens)

    def run(self, **kwargs):

        self.__call__(**kwargs)

        e_out = self._out_prep_func(self)

        self._qout.put(e_out)


class FullPipeline(SourcePipeline):

    def __init__(self, name, comp_graph, q_in, q_out, event_dispatcher, out_prep_func, frozen_tokens=None):

        self._qin = q_in
        self._loop = EventLoop(q_in, self, event_dispatcher)

        super(FullPipeline, self).__init__(name, comp_graph, q_out, out_prep_func, frozen_tokens)

    def listen(self):
        self._loop.start()

    def stop(self):
        self._loop.stop()
        self._loop.join()
        Pipeline.stop(self)

    @property
    def loop(self):
        return self._loop

