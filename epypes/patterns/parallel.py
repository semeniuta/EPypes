from epypes.pipeline import Pipeline, SourcePipeline, SinkPipeline, FullPipeline
from epypes.node import Node
from epypes.payload import split_payload_and_build_tokens
from epypes.util import make_full_pipeline

import multiprocessing as mp

def create_ppnode_from_func(f, input_splitter, num=mp.cpu_count()):

    fname = f.__name__
    par_nodes = [Node('{0}_{1}Node'.format(fname, i), f) for i in range(num)]

    name ='{0}_PPNode'.format(fname)
    ppnode = create_ppnode_from_nodes(name, par_nodes, input_splitter)

    return ppnode

def create_ppnode_from_nodes(name, nodes, input_splitter):
    '''
    Creates a ParallelPipesNode from a list nodes intended
    for parallel execution.

    Typical application is image acquisition, synchronized on event.
    In this case, nodes should be created as
    instances of vision.CameraGrabNode
    '''

    s_pipelines = []
    for nd in nodes:
        pname = '{}_Pipeline'.format(nd.name)
        pipe = Pipeline(pname, [nd])
        s_pipelines.append(pipe)

    return ParallelPipesNode(name, s_pipelines, input_splitter)

class ParallelPipesNode(Node):
    '''
    A node with a number of paralelly-run pipelines inside, each
    running in a separate process. A token supplied
    to run method of an instance of ParallelPipesNode
    is further forwarded or splitted to each of the enclosed pipelines
    in accordance with the logic in the supplied input_splitter function
    '''

    def __init__(self, name, pipelines, input_splitter, payload_index=None):

        self._n_parallel = len(pipelines)
        self._indices = range(self._n_parallel)

        self._input_queues = [mp.Queue() for i in self._indices]
        self._qout = mp.Queue()

        self._input_splitter = input_splitter

        self._payload_index =payload_index

        self._par_pipes = []
        for i in self._indices:

            qin = self._input_queues[i]
            pipe, _, _ = make_full_pipeline(pipelines[i], (qin, self._qout))

            self._par_pipes.append(pipe)
            pipe.listen()

        def node_func(token=None):

            token_parts = split_payload_and_build_tokens(token, self._input_splitter, self._n_parallel, self._payload_index)

            for i, tk in enumerate(token_parts):
                self._input_queues[i].put(tk)

            res = [(i, self._qout.get()) for i in self._indices]
            res = sorted(res, key=(lambda tup: tup[0]))

            return tuple(res)

        Node.__init__(self, name, node_func)

    def traverse_time(self):
        inner = tuple(ppipe.traverse_time() for ppipe in self.par_pipelines)
        return self.name, self.time, inner

    @property
    def par_pipelines(self):
        return self._par_pipes

    def request_stop(self):
        for pipe in self._par_pipes:
            pipe.request_stop()

class ParallelPipesNodeSim(ParallelPipesNode):
    '''
    A serial simulator of the ParallelPipesNode class.
    Everything runs serially in a single process
    while the API is retained
    '''

    def __init__(self, name, pipelines, input_splitter, payload_index=None):

        self._n_parallel =len(pipelines)
        self._indices = range(self._n_parallel)
        self._input_splitter = input_splitter
        self._payload_index = payload_index
        self._par_pipes = pipelines

        def node_func(token=None):

            token_parts = split_payload_and_build_tokens(token, self._input_splitter, self._n_parallel, self._payload_index)

            res = ((i, self._par_pipes[i].run(token_parts[i])) for i in self._indices)

            return tuple(res)

        Node.__init__(self, name, node_func)
