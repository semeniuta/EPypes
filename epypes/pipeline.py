'''
Implementation of pipeline classes and related functions
'''

from __future__ import print_function

from epypes.node import Node
from epypes.loop import EventLoop

import time

def run_and_put_to_q(pipeline_object, token, q):
    res = Pipeline.run(pipeline_object, token)
    q.put(res)

def is_exception(token):
    return issubclass(type(token), Exception)

def state_change_while_stopping(method):
    def wrapper(*args, **kvargs):
        self = args[0]
        self._state = 'stopping'
        res = method(*args, **kvargs)
        self._state = 'stopped'
        return res
    return wrapper

class Pipeline(Node):

    def __init__(self, name, nodes):
        self._add_nodes(nodes)
        self._outputs = {node.name: None for node in self.nodes}
        self._exception = None
        Node.__init__(self, name, self._get_master_func())

    @property
    def nodes(self):
        return self._nodes

    def modify_node_argument(self, node_name, key, new_value):
        node = self.get_node_by_name(node_name)
        node.modify_argument(key, new_value)

    def get_node_by_index(self, node_index):
        if node_index < 0 or node_index > len(self._nodes):
            raise IndexError('The provided node index is out of range')

        return self._nodes[node_index]

    def get_node_by_name(self, node_name):
        if node_name not in self._node_indices:
            raise KeyError('The such node exists')

        node_index = self._node_indices[node_name]
        return self._nodes[node_index]

    def handle_exception(self, exception, node):
        raise exception

    def traverse_time(self):
        return (self.name, self.time, tuple(nd.traverse_time() for nd in self.nodes))

    def out(self, node_name):
        return self._outputs[node_name]

    def request_stop(self):
        self._wait_to_state_ready()
        self._stop_nodes()
        self._state = 'stopped'

    def _wait_to_state_ready(self):
        while self._state is not 'ready':
            time.sleep(0.1)

    def _stop_nodes(self):
        for node in self.nodes:
            node.request_stop()

    def _add_nodes(self, nodes):

        self._nodes = []
        self._node_indices = dict()
        for i, nd in enumerate(nodes):
            if nd.name in self._node_indices:
                raise Exception('Duplicate node name found: "{0}"'.format(nd.name))
            self._nodes.append(nd)
            self._node_indices[nd.name] = i

    def _get_master_func(self):

        def mf(token=None):

            exception_occured = False
            exception_node = None

            for node in self.nodes:
                token = node.run(token)
                if is_exception(token):
                    exception_occured = True
                    exception_node = node
                    break
                else:
                    self._store_token(node.name, token)

            if exception_occured:
                self.handle_exception(token, exception_node)
                return None

            return token

        return mf

    def _store_token(self, node_name, token):
        self._outputs[node_name] = token

    def __repr__(self):
        r = Node.__repr__(self)

        nodes_str = ''
        for node in self.nodes[:-1]:
            nodes_str += '{0} -> '.format(node.name)
        nodes_str += self.nodes[-1].name

        return '{0}: {1}'.format(r, nodes_str)

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
        self._wait_to_state_ready()
        self._loop.request_stop()
        self._loop.join()
        self._stop_nodes()
        self._state = 'stopped'

class FullPipeline(SinkPipeline):

    def __init__(self, name, nodes, q_in, q_out):
        SinkPipeline.__init__(self, name, nodes, q_in)

        self._qout = q_out

    def run(self, token=None):
        run_and_put_to_q(self, token, self._qout)

if __name__ == '__main__':
    pass
