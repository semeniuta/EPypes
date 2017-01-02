'''
Implementaion of basic pipeline entities and related functions
'''

from __future__ import print_function

import sys
ver = sys.version_info[:2]
if ver[0] == 2:
    import Queue as queue
else:
    import queue

from epypes.commons import GenericObject

import threading
import multiprocessing as mp
import time

#Queue = queue.Queue
Queue = mp.Queue

class Node(GenericObject):

    def __init__(self, name, func, **kvargs):
        GenericObject.__init__(self, name)
        self._func = func
        self._kvargs = kvargs
        self._time = None

    def modify_argument(self, key, new_value):

        if key not in self._kvargs:
            raise Exception('Incorrect argument key')

        self._kvargs[key] = new_value

    def run(self, token=None):
        t0 = time.time()

        if token is None:
            res = self._func(**self._kvargs)
        res = self._func(token, **self._kvargs)

        t1 = time.time()
        self._time = t1 - t0

        return res

    @property
    def time(self):
        if self._time is None:
            msg = '{} has not yet ran, but time requested'.format(self.name)
            raise Exception(msg)
        return self._time

    def request_stop(self):
        pass

    def get_arguments(self):
        return self._kvargs

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
            for i, node in enumerate(self._nodes):
                token = node.run(token)
                self._store_token(node.name, token)
            return token
        return mf

    def _store_token(self, node_name, token):
        self._outputs[node_name] = token

    @property
    def nodes(self):
        return self._nodes

    def run(self, token=None):
        return Node.run(self, token)

    def out(self, node_name):
        return self._outputs[node_name]

    def request_stop(self):
        for node in self._nodes:
            node.request_stop()

def run_and_put_to_q(pipeline_object, token, q):
    res = SimplePipeline.run(pipeline_object, token)
    q.put(res)


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
        self._loop = AcceptLoop(q_in, self)

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

def make_pipeline(simple_pipeline, queues=()):
    if queues == ():
        qin = Queue()
        qout = Queue()
    else:
        qin, qout = queues

    name = simple_pipeline.name
    nodes = simple_pipeline.nodes
    pipe = Pipeline(name, nodes, qin, qout)

    return pipe, qin, qout

def basic_eventloop(callback_node, token_q, stop_q):
    while True:
        if not stop_q.empty():
            stop_q.get()
            break

        if not token_q.empty():
            token = token_q.get()
            callback_node.run(token)

class AcceptLoop(GenericObject):

    def __init__(self, q, callback_node):
        name = 'In{}'.format(callback_node.__class__.__name__)
        GenericObject.__init__(self, name)

        self._callback_node = callback_node
        self._token_q = q
        self._stop_q = Queue()

        t_args = (self._callback_node, self._token_q, self._stop_q)
        self._thread = threading.Thread(target=basic_eventloop, args=t_args)

    def start(self):
        self._thread.start()

    def request_stop(self):
        self._stop_q.put(None)
        self._thread.join()

if __name__ == '__main__':

    def say_hello(to_whom, exclamation=False):
        s = 'Hello ' + to_whom
        if exclamation:
            s += '!'
        return s

    g = Node('Greeter', say_hello, exclamation=False)
    p = Node('Capitalizer', lambda x: x.upper())

    spipe = SimplePipeline('MyPipe', [g, p])
    pipe, qin, qout = make_pipeline(spipe)

    print_node = Node('Printer', lambda x: print(x))
    pipe_out = SinkPipeline('PrinterPipe', [print_node], qout)

    pipe.listen()
    pipe_out.listen()
