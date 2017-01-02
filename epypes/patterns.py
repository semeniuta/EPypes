from epypes.pipeline import Node, SimplePipeline, SourcePipeline, SinkPipeline, Pipeline

import multiprocessing as mp
from multiprocessing import Queue
import concurrent.futures as cf
from concurrent.futures import ProcessPoolExecutor

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

    def __init__(self, name, par_nodes):

        self._indices = range(len(par_nodes))
        self._input_queues = [Queue() for i in self._indices]
        self._qout = Queue()

        self._par_pipes = []
        for i in self._indices:
            pname = '{}_Pipeline'.format(par_nodes[i].name)
            qin = self._input_queues[i]
            pipe = Pipeline(name, [par_nodes[i]], qin, self._qout, mp.Process)
            self._par_pipes.append(pipe)
            pipe.listen()

        def node_func(event_token):
            res = []
            for qin in self._input_queues:
                qin.put(event_token)

            res = [(i, self._qout.get()) for i in self._indices]
            res = sorted(res, key=(lambda tup: tup[0]))

            return tuple(res)

        Node.__init__(self, name, node_func)

    def request_stop(self):
        for pipe in self._par_pipes:
            pipe.request_stop()

class ProcessWorkersPoolNode(Node):
    '''
    Assumes that a token is an iterable ocntaining objects of the same type
    '''

    def __init__(self, name, worker_function, n_workers=mp.cpu_count()):

        self._n_workers = n_workers
        self._worker_function = worker_function

        def node_func(iterable_token):

            with ProcessPoolExecutor(max_workers=self._n_workers) as executor:

                futures_dict = {}
                for el in iterable_token:
                    f = executor.submit(self._worker_function, el)
                    futures_dict[f] = el

                res = {}
                for f in cf.as_completed(futures_dict):
                    el = futures_dict[f]
                    res[el] = f.result()

            return res

        Node.__init__(self, name, node_func)


    def n_workers(self):
        return self._n_workers

class ProcessWorkersPoolNodeWithMap(ProcessWorkersPoolNode):
    '''
    The same as ProcessWorkersPoolNode, but uses executor.map
    instead of executor.submit
    '''

    def __init__(self, name, worker_function, n_workers=mp.cpu_count()):

        self._n_workers = n_workers
        self._worker_function = worker_function

        def node_func(iterable_token):

            with ProcessPoolExecutor(max_workers=self._n_workers) as executor:
                res = zip(iterable_token, executor.map(self._worker_function, iterable_token))

            return dict(res)

        Node.__init__(self, name, node_func)

if __name__ == '__main__':
    pass
