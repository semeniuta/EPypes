from epypes.pipeline import SimplePipeline, SourcePipeline, SinkPipeline, Pipeline, make_pipeline
from epypes.node import Node

import multiprocessing as mp

def par_pipes_node_from_func(f, num=mp.cpu_count()):

    fname = f.__name__
    par_nodes = [Node('Func({0}_{1})Pipeline'.format(fname, i)) for i in range(num)]

    return ParallelPipesNode('ParallelFunction[{0}]'.format(fname), par_nodes)

def copy_input_splitter(token, n_parallel):
    return tuple((token for i in range(n_parallel)))

def elementwise_input_splitter(token, n_parallel):
    if len(token) != n_parallel:
        raise Exception('Number of elements in the token is not equal to the number of parallel taksk')
    return tuple(token)

class ParallelPipesNode(Node):
    '''
    A node with a number of paralelly-run pipelines inside, each
    constructed around the correspondign node in the supplied
    par_nodes and running in a separate process. A token supplied
    to run method an instance of ParallelPipesNode is further forwarded to
    each of the enclosed pipelines.

    Typical application of ParallelPipesNode is image acquisition,
    synchronized on event. In this case, par_nodes should be created as
    instances of vision.CameraGrabNode
    '''

    def __init__(self, name, par_nodes, input_splitter):

        self._n_parallel =len(par_nodes)
        self._indices = range(self._n_parallel)
        self._input_queues = [mp.Queue() for i in self._indices]
        self._qout = mp.Queue()
        self._input_splitter = input_splitter

        self._par_pipes = []
        for i in self._indices:

            qin = self._input_queues[i]

            pname = '{}_Pipeline'.format(par_nodes[i].name)
            pipe = Pipeline(pname, [par_nodes[i]], qin, self._qout)

            self._par_pipes.append(pipe)
            pipe.listen()

        def node_func(event_token):
            res = []

            token_parts = self._input_splitter(event_token, self._n_parallel)

            for i, tk in enumerate(token_parts):
                self._input_queues[i].put(tk)

            res = [(i, self._qout.get()) for i in self._indices]
            #res = sorted(res, key=(lambda tup: tup[0]))

            return tuple(res)

        Node.__init__(self, name, node_func)

    def request_stop(self):
        for pipe in self._par_pipes:
            pipe.request_stop()


class NewParallelPipesNode(Node):

    def __init__(self, name, simple_pipelines, input_splitter):

        self._n_parallel =len(simple_pipelines)
        self._indices = range(self._n_parallel)

        self._input_queues = [mp.Queue() for i in self._indices]
        self._qout = mp.Queue()

        self._input_splitter = input_splitter

        self._par_pipes = []
        for i in self._indices:

            qin = self._input_queues[i]
            pipe, _, _ = make_pipeline(simple_pipelines[i], (qin, self._qout))

            self._par_pipes.append(pipe)
            pipe.listen()

        def node_func(event_token=None):
            res = []

            token_parts = self._input_splitter(event_token, self._n_parallel)

            for i, tk in enumerate(token_parts):
                self._input_queues[i].put(tk)

            res = [(i, self._qout.get()) for i in self._indices]
            res = sorted(res, key=(lambda tup: tup[0]))

            return tuple(res)

        Node.__init__(self, name, node_func)

    def request_stop(self):
        for pipe in self._par_pipes:
            pipe.request_stop()

if __name__ == '__main__':
    pass
