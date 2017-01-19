'''
Implementaion of basic pipeline entities and related functions
'''

from __future__ import print_function

from epypes.node import Node
from epypes.loop import EventLoop

import multiprocessing as mp

def make_pipeline(simple_pipeline, queues=()):
    if queues == ():
        qin = mp.Queue()
        qout = mp.Queue()
    else:
        qin, qout = queues

    name = simple_pipeline.name
    nodes = simple_pipeline.nodes
    pipe = Pipeline(name, nodes, qin, qout)

    return pipe, qin, qout

def run_and_put_to_q(pipeline_object, token, q):
    res = SimplePipeline.run(pipeline_object, token)
    q.put(res)

class SimplePipeline(Node):

    def __init__(self, name, nodes):
        master_function = self._get_master_func()
        Node.__init__(self, name, master_function)
        self._nodes = list(nodes)
        self._outputs = {node.name: None for node in self._nodes}

    def __repr__(self):
        r = Node.__repr__(self)

        nodes_str = ''
        for node in self.nodes[:-1]:
            nodes_str += '{0} -> '.format(node.name)
        nodes_str += self.nodes[-1].name

        return '{0}: {1}'.format(r, nodes_str)

    def _get_master_func(self):
        def mf(token=None):
            for node in self.nodes:
                token = node.run(token)
                self._store_token(node.name, token)
            return token
        return mf

    def _store_token(self, node_name, token):
        self._outputs[node_name] = token

    def traverse_time(self):
        return (self.name, self.time, tuple(nd.traverse_time() for nd in self.nodes))

    @property
    def nodes(self):
        return self._nodes

    @property
    def node_times(self):
        return [nd.time for nd in self.nodes]

    def out(self, node_name):
        return self._outputs[node_name]

    def request_stop(self):
        for node in self._nodes:
            node.request_stop()

class SourcePipeline(SimplePipeline):
    def __init__(self, name, nodes, q_out):
        SimplePipeline.__init__(self, name, nodes)
        self._qout = q_out

    def run(self, token):
        run_and_put_to_q(self, token, self._qout)


class SinkPipeline(SimplePipeline):
    def __init__(self, name, nodes, q_in):
        SimplePipeline.__init__(self, name, nodes)

        self._qin = q_in
        self._loop = EventLoop(q_in, self)

    def listen(self):
        self._loop.start()

    def request_stop(self):
        SimplePipeline.request_stop(self)
        self._loop.request_stop()

class Pipeline(SinkPipeline):

    def __init__(self, name, nodes, q_in, q_out):
        SinkPipeline.__init__(self, name, nodes, q_in)

        self._qout = q_out

    def run(self, token):
        run_and_put_to_q(self, token, self._qout)

if __name__ == '__main__':
    pass
