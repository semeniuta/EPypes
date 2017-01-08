from epypes.node import Node

import multiprocessing as mp
import concurrent.futures as cf

class ProcessWorkersPoolNode(Node):
    '''
    Assumes that a token is an iterable containing objects of the same type
    '''

    def __init__(self, name, worker_function, n_workers=mp.cpu_count()):

        self._n_workers = n_workers
        self._worker_function = worker_function

        def node_func(iterable_token):

            with cf.ProcessPoolExecutor(max_workers=self._n_workers) as executor:

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

            with cf.ProcessPoolExecutor(max_workers=self._n_workers) as executor:
                res = zip(iterable_token, executor.map(self._worker_function, iterable_token))

            return dict(res)

        Node.__init__(self, name, node_func)