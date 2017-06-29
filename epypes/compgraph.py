#
# Directed acycling graph
#

from epypes.node import Node
import networkx as nx

def create_set_of_vertices(vertices):
    V = set()
    for v in vertices:
        V.add(v)
    return V

def create_nodes_from_comp_graph(cg):

    nodes = dict()
    for fname, f in cg.functions.items():
        nodes[fname] = Node(fname, f)

    return nodes

class UnderfinedSourceTokensException(Exception):
    pass

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


class FunctionPlaceholder(object):

    def __call__(self, *args, **kwargs):
        raise Exception('FunctionPlaceholder can not be run by itself')


class CompGraph(object):

    def __init__(self, func_dict, func_io):

        self._functions = func_dict
        self._func_io = func_io

        fnames = self._functions.keys()
        self._inputs = {fname: [] for fname in fnames}
        self._outputs = {fname: [] for fname in fnames}

        self._src_tokens = None
        self._snk_tokens = None

        token_names = set()
        edges = []
        for fname in func_io:

            if fname not in func_dict:
                raise Exception('{} is not in set of functions')
            f_in, f_out = func_io[fname]

            if type(f_in) is tuple:
                for arg in f_in:
                    token_names.add(arg)
                    edges.append((arg, fname))
                    self._inputs[fname].append(arg)
            else:
                token_names.add(f_in)
                edges.append((f_in, fname))
                self._inputs[fname].append(f_in)

            if type(f_out) is tuple:
                for arg in f_out:
                    token_names.add(arg)
                    edges.append((fname, arg))
                    self._outputs[fname].append(arg)
            else:
                token_names.add(f_out)
                edges.append((fname, f_out))
                self._outputs[fname].append(f_out)

        self._G = BipartiteDigraph(fnames, token_names, edges)

    def func_inputs(self, func_name):
        return self._inputs[func_name]

    def func_outputs(self, func_name):
        return self._outputs[func_name]

    def to_networkx(self, func_v_attr={}, token_v_attr={}, edge_attr={}):

        default_func_v_attr = {'shape': 'rect'}
        for k in default_func_v_attr.keys():
            if k not in func_v_attr:
                func_v_attr[k] = default_func_v_attr[k]

        return self._G.to_networkx(vert1_attr=func_v_attr, vert2_attr=token_v_attr, edge_attr=edge_attr)


    @property
    def graph(self):
        return self._G

    @property
    def functions(self):
        return self._functions

    @property
    def func_io(self):
        return self._func_io

    @property
    def tokens(self):
        return self._G.vertices2

    @property
    def source_tokens(self):

        if self._src_tokens is not None:
            return self._src_tokens
        else:
            res = []
            for tk in self.tokens:
                if self._G.is_source_vertex(tk):
                    res.append(tk)
            self._src_tokens = set(res)
            return self._src_tokens

    @property
    def sink_tokens(self):

        if self._snk_tokens is not None:
            return self._snk_tokens
        else:
            res = []
            for tk in self.tokens:
                if self._G.is_sink_vertex(tk):
                    res.append(tk)
            self._snk_tokens = set(res)
            return self._snk_tokens


    def to_cg_with_nodes(self):
        nodes = create_nodes_from_comp_graph(self)
        cg_with_nodes = NodeBasedCompGraph(func_dict=nodes, func_io=self._func_io)
        return cg_with_nodes

class NodeBasedCompGraph(CompGraph):

    def swap(self, node_name, new_node):
        self._functions[node_name] = new_node

    @property
    def nodes(self):
        return self.functions

class TokenManager(object):

    def __init__(self, cg):
        self._cg = cg
        self._values = {tk: None for tk in cg.tokens}
        self._free = set(cg.tokens)
        self._frozen = set()

    def freeze_token(self, token_name, token_value):

        if token_name not in self._cg.tokens:
            raise Exception('{} is not a valid token name'.format(token_name))

        self._values[token_name] = token_value

        if token_name in self._free:
            self._free.remove(token_name)
            self._frozen.add(token_name)

    def save_payload_value(self, token_name, token_value):
        if token_name in self._frozen:
            raise Exception('{} is a hyperparameter'.format(token_name))

        self._values[token_name] = token_value

    def token_value(self, token_name):
        if token_name not in self._cg.tokens:
            raise Exception('{} is not a valid token name'.format(token_name))

        return self._values[token_name]

    def to_networkx(self, func_v_attr={}, free_token_v_attr={}, frozen_token_v_attr={}, edge_attr={}):


        default_frozen_token_v_attr = {
            'style': 'filled',
            'fillcolor': 'gray'
        }

        for k in default_frozen_token_v_attr.keys():
            if k not in frozen_token_v_attr:
                frozen_token_v_attr[k] = default_frozen_token_v_attr[k]

        nxg = self._cg.to_networkx(func_v_attr=func_v_attr, edge_attr=edge_attr)

        for frozen_token_v in self.frozen:
            this_node = nxg.node[frozen_token_v]
            for k, v in frozen_token_v_attr.items():
                this_node[k] = v

        for free_token_v in self.free:
            this_node = nxg.node[free_token_v]
            for k, v in free_token_v_attr.items():
                this_node[k] = v

        return nxg

    @property
    def frozen_values(self):
        return {tk: self._values[tk] for tk in self._frozen}

    @property
    def frozen(self):
        return self._frozen

    @property
    def free(self):
        return self._free

    @property
    def free_source_tokens(self):
        return self._free.intersection(self._cg.source_tokens)


class CompGraphRunner(object):

    def __init__(self, cg, frozen_tokens=None):
        self._cg = cg
        self._torder = DepthFirstOrder(self._cg.graph).topological_order
        self._tm = TokenManager(self._cg)

        self._frozen_tokens = frozen_tokens
        if frozen_tokens is not None:
            for tk, tk_val in frozen_tokens.items():
                self._tm.freeze_token(tk, tk_val)

    def run(self, **kvargs):

        kvargs_set = set(kvargs.keys())
        if not self._tm.free_source_tokens.issubset(kvargs_set):
            raise UnderfinedSourceTokensException()
            #raise Exception('Some source tokens have undefined value')

        for v in self._torder:

            if v in kvargs:
                self._tm.save_payload_value(v, kvargs[v])

            elif v in self._cg.functions:

                f = self._cg.functions[v]
                f_args = [self._tm.token_value(token_name) for token_name in self._cg.func_inputs(v)]
                f_out = f(*f_args)

                v_adj = self._cg.graph.adj(v)
                if len(v_adj) == 1:
                    payload_token_name = v_adj[0]
                    self._tm.save_payload_value(payload_token_name, f_out)
                elif len(v_adj) > 1:
                    for i, tk in enumerate(v_adj):
                        self._tm.save_payload_value(tk, f_out[i])

            else:
                pass

    def freeze_token(self, token_name, token_value):
        self._tm.freeze_token(token_name, token_value)

    def token_value(self, token_name):
        return self._tm.token_value(token_name)

    @property
    def frozen_tokens(self):
        return self._frozen_tokens

    @property
    def required_source_tokens(self):
        return self._tm.free_source_tokens

    @property
    def token_manager(self):
        return self._tm







