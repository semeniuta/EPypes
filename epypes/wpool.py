from epypes.node import Node
from epypes.pipeline import Pipeline

import multiprocessing as mp
import concurrent.futures as cf

def wpool_node_from_cgraph(name, cg, frozen_tokens, target_input_token, tokens_to_get):

    pipe = Pipeline(name, cg, frozen_tokens)

    if pipe.runner.token_manager.free_source_tokens != {target_input_token}:
        raise Exception('Free tokens other than target_input_token exist')

    def func(item):
        res = pipe.run(tokens_to_get, **{target_input_token: item})
        return res


    wpn_name = '{}WPool'.format(name)
    wpn = ProcessWorkersPoolNode(wpn_name, func)

    return wpn


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

                res_dict = {}
                for f in cf.as_completed(futures_dict):
                    el = futures_dict[f]
                    res_dict[el] = f.result()

            return tuple(res_dict[el] for el in iterable_token)

        Node.__init__(self, name, node_func)


    def n_workers(self):
        return self._n_workers

class ProcessWorkersPoolNodeSim(ProcessWorkersPoolNode):

    def __init__(self, name, worker_function, n_workers=mp.cpu_count()):

        self._n_workers = n_workers #fictional
        self._worker_function = worker_function

        def node_func(iterable_token):
            return tuple(worker_function(el) for el in iterable_token)

        Node.__init__(self, name, node_func)


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
                #res = zip(iterable_token, executor.map(self._worker_function, iterable_token))
                res = executor.map(self._worker_function, iterable_token)

            return tuple(res)

        Node.__init__(self, name, node_func)
