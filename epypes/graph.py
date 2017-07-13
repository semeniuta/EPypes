import networkx as nx

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

    def is_sink_vertex(self, v):
        if self._adj[v] == []:
            return True
        return False

    def preceding_vertices(self, v):
        remaining_vertices = self._V.difference([v])
        res = []
        for v0 in remaining_vertices:
            if v in self.adj(v0):
                res.append(v0)
        return res

    def to_networkx(self, vert_attr={}, edge_attr={}):
        # Attributes from:
        # http://www.graphviz.org/doc/info/attrs.html

        nxg = nx.DiGraph()

        nxg.add_nodes_from(self._V, **vert_attr)
        for v in self._V:
            for w in self._adj[v]:
                nxg.add_edge(v, w, **edge_attr)

        return nxg

    def __repr__(self):
        return str(self._adj)

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

    def to_networkx(self, vert1_attr={}, vert2_attr={}, edge_attr={}):

        nxg = nx.DiGraph()

        nxg.add_nodes_from(self._V1, bipartite=0, **vert1_attr)
        nxg.add_nodes_from(self._V2, bipartite=1, **vert2_attr)

        for v in self._V:
            for w in self._adj[v]:
                nxg.add_edge(v, w, **edge_attr)

        return nxg

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
    def topological_order(self):
        return list(reversed(self._post))
