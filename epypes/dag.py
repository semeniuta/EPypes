#
# Directed acycling graph
#

import inspect

def create_set_of_vertices(vertices):
    V = set()
    for v in vertices:
        V.add(v)
    return V

class Digraph(object):

    def __init__(self, vertices, edges=None):

        self._V = create_set_of_vertices(vertices)

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

    def is_source_vertex(self, v):
        remaining_vertices = self._V.difference([v])
        for v0 in remaining_vertices:
            if v in self.adj(v0):
                return False
        return True

    def preceding_vertices(self, v):
        remaining_vertices = self._V.difference([v])
        res = []
        for v0 in remaining_vertices:
            if v in self.adj(v0):
                res.append(v0)
        return res

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

class BipartiteDigraph(Digraph):

    def __init__(self, vertices1, vertices2, edges=None):

        self._V1 = create_set_of_vertices(vertices1)
        self._V2 = create_set_of_vertices(vertices2)

        all_vertices = self._V1.union(self._V2)
        Digraph.__init__(self, all_vertices, edges)

    def add_edge(self, a, b):

        if not self._vertices_in_different_sets(a, b):
            raise Exception('{0} -> {1} is not a valid edge'.format(a, b))

        Digraph.add_edge(self, a, b)

    @property
    def vertices1(self):
        return self._V1

    @property
    def vertices2(self):
        return self._V2

    def _vertices_in_different_sets(self, a, b):
        return (a in self._V1 and b in self._V2) or (a in self._V2 and b in self._V1)





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


class ComputationalGraph(object):

    def __init__(self, functions, token_names):

        self._functions = {f.__name__ : f for f in functions}
        # does not account for usage of the same function multiple times

        self._frozen = dict()

        fnames = self._functions.keys()
        self._G = BipartiteDigraph(fnames, token_names)
        self._dfo = DepthFirstOrder(self._G)

    def input_to(self, func_name, token_name):
        self._G.add_edge(token_name, func_name)

    def output_from(self, func_name, token_name):
        self._G.add_edge(func_name, token_name)

    def freeze_token(self, token_name, token_value):
        self._frozen[token_name] = token_value

    def source_tokens(self, payload_only=True):
        res = []
        for tk in self.tokens_set:
            if self._G.is_source_vertex(tk):
                if (payload_only and not tk in self.frozen) or not payload_only:
                    res.append(tk)
        return set(res)

    def run(self, **kvargs):

        res = dict()
        for v in reversed(self._dfo.postorder):
            if v in self._frozen:
                res[v] = self._frozen[v]
            elif v in kvargs:
                res[v] = kvargs[v]
            elif v in self._functions:
                f = self._functions[v]
                f_kvargs = {k: res[k] for k in self._G.preceding_vertices(v)}
                f_out = f(**f_kvargs)
                v_adj = self._G.adj(v)
                if len(v_adj) == 1:
                    res[v_adj[0]] = f_out
                elif len(v_adj) > 1:
                    for i, tk in enumerate(v_adj):
                        res[tk] = f_out[i]

        return res



    @property
    def functions_set(self):
        return self._G.vertices1

    @property
    def tokens_set(self):
        return self._G.vertices2

    @property
    def frozen(self):
        return self._frozen

if __name__ == '__main__':
    print('Test')






