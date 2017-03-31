'''
Implementation of pipeline classes and related functions
'''

from __future__ import print_function

from epypes.node import Node
from epypes.loop import EventLoop
from epypes.dag import CompGraphRunner

def run_and_put_to_q(pipeline_object, token, q):
    res = Pipeline.run(pipeline_object, token)
    q.put(res)

def is_exception(token):
    return issubclass(type(token), Exception)

class Pipeline(Node):

    def __init__(self, name, comp_graph, frozen_tokens):
        self._cg = comp_graph.to_cg_with_nodes()
        self._runner = CompGraphRunner(self._cg, frozen_tokens)

        def master_function(**kvargs):
            self._runner.run(**kvargs)

        Node.__init__(self, name, master_function)

    def run(self, **kvargs):
        self.__call__(**kvargs)

    @property
    def nodes(self):
        return self._cg.nodes

    def modify_frozen_token(self, token_name, new_value):
        self._runner.freeze_token(token_name, new_value)

    def traverse_time(self):
        return (self.name, self.time, tuple(nd.traverse_time() for nd in self.nodes))

    def token_value(self, token_name):
        return self._runner.token_value(token_name)

    def request_stop(self):
        for node in self.nodes:
            node.request_stop()

class SourcePipeline(Pipeline):
    def __init__(self, name, nodes, q_out):
        self._qout = q_out
        Pipeline.__init__(self, name, nodes)

    def run(self, token=None):
        run_and_put_to_q(self, token, self._qout)

class SinkPipeline(Pipeline):
    def __init__(self, name, nodes, q_in):
        self._qin = q_in
        self._loop = EventLoop(q_in, self)
        Pipeline.__init__(self, name, nodes)

    def listen(self):
        self._loop.start()

    def request_stop(self):
        self._loop.request_stop()
        self._loop.join()
        Pipeline.request_stop(self)

class FullPipeline(SinkPipeline):

    def __init__(self, name, nodes, q_in, q_out):
        SinkPipeline.__init__(self, name, nodes, q_in)

        self._qout = q_out

    def run(self, token=None):
        run_and_put_to_q(self, token, self._qout)

if __name__ == '__main__':
    pass
