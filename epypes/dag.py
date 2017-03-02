#
# Directed acycling graph
#

import inspect

class Digraph(object):

    def __init__(self, vertices, edges=None):

        self._V = set()
        for v in vertices:
            self._V.add(v)

        self._num_vertices = 0
        self._adj = dict()
        for v in self._V:
            self._adj[v] = []
            self._num_vertices += 1

        self._num_edges = 0
        if edges is not None:
            for a, b in edges:
                self.add_edge(a, b)

    def add_edge(self, a, b):

        self._verify_if_vertice_in_set(a)
        self._verify_if_vertice_in_set(b)

        self._adj[a].append(b)
        self._num_edges += 1

    def reverse(self):

        reversed_digraph = Digraph(self._V)

        for v in self._adj:
            for w in self._adj[v]:
                reversed_digraph.add_edge(w, v)

        return reversed_digraph

    def adj(self, v):
        return self._adj[v]

    @property
    def vertices(self):
        return self._V

    @property
    def num_vertices(self):
        return self._num_vertices

    @property
    def num_edges(self):
        return self._num_edges

    def _verify_if_vertice_in_set(self, v):
        if v not in self._V:
            raise Exception('{} is not a part of the set of vertices'.format(v))

class DepthFirstSearch(object):

    def __init__(self, graph):
        self._G = graph
        self._marked = {v: False for v in graph.vertices}
        self._edge_to = {v: None for v in graph.vertices}

    def dfs(self, v):
        self.on_entry(v)

        self._marked[v] = True

        for w in self._G.adj(v):
            if not self._marked[w]:
                self._edge_to[w] = v
                self.dfs(w)

        self.on_exit(v)

    def run_dfs_on_all(self):
        for v in self._G.vertices:
            if not self._marked[v]:
                self.dfs(v)

    def on_entry(self, v):
        pass

    def on_exit(self, v):
        pass

class DirectedCycle(DepthFirstSearch):

    def __init__(self, graph):

        self._on_stack = {v: False for v in graph.vertices}
        self._cycle_path = None
        DepthFirstSearch.__init__(self, graph)
        self.run_dfs_on_all()

    def dfs(self, v):
        self.on_entry(v)

        for w in self._G.adj(v):

            self._marked[v] = True

            if self.has_cycle():
                return
            elif not self._marked[w]:
                self._edge_to[w] = v
                self.dfs(w)
            elif self._on_stack[w]:
                cycle_back = []
                x = v
                while x != w:
                    cycle_back.append(x)
                    x = self._edge_to[x]
                cycle_back.append(w)
                cycle_back.append(v)
                cycle_back.reverse()
                self._cycle_path = cycle_back

        self.on_exit(v)

    def has_cycle(self):
        return self._cycle_path is not None

    @property
    def cycle(self):
        return self._cycle_path

    def on_entry(self, v):
        self._on_stack[v] = True

    def on_exit(self, v):
        self._on_stack[v] = False

class DepthFirstOrder(DepthFirstSearch):

    def __init__(self, graph):
        self._pre = []
        self._post = []
        DepthFirstSearch.__init__(self, graph)
        self.run_dfs_on_all()

    def on_entry(self, v):
        self._pre.append(v)

    def on_exit(self, v):
        self._post.append(v)

    @property
    def preorder(self):
        return self._pre

    @property
    def postorder(self):
        return self._post

    @property
    def reverse_postorder(self):
        return reversed(self._post)


class ComputationalGraph(Digraph):

    def __init__(self, functions, token_names):

        self._functions = {f.__name__ : f for f in functions}
        # does not account for usage of the same function multiple times

        all_names = list(self._functions.keys()) + token_names
        Digraph.__init__(self, all_names)


if __name__ == '__main__':
    print('Test')






