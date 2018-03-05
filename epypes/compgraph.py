from epypes.node import Node
from epypes.graph import BipartiteDigraph, DepthFirstOrder

def rename_in_dict(d, old_key, new_key):

    d[new_key] = d[old_key]
    del d[old_key]


def common_func_names_exist(cg1, cg2):
    keys1 = cg1.func_io.keys()
    keys2 = cg2.func_io.keys()
    if set(keys1).intersection(keys2) == set():
        return False
    return True

def add_suffix_to_dict_values(d, key, suffix, exclude_suffixing=None):

    def rename(obj):

        if exclude_suffixing is not None and obj in exclude_suffixing:
            return  obj

        if type(obj) is str:
            return obj + suffix

        return tuple(rename(el) for el in obj)

    return tuple(rename(el) for el in d[key])

def merge_dicts(d1, d2, suffix_1=None, suffix_2=None, rename_values=False, exclude_value_suffixing=None):

    if suffix_1 is not None:
        res = dict()
        for k in d1:
            new_k = k + suffix_1
            if rename_values:
                val = add_suffix_to_dict_values(d1, k, suffix_1, exclude_value_suffixing)
            else:
                val = d1[k]
            res[new_k] = val
    else:
        res = d1.copy()

    if suffix_2 is not None:
        for k in d2:
            new_k = k + suffix_2
            if rename_values:
                val = add_suffix_to_dict_values(d2, k, suffix_2, exclude_value_suffixing)
            else:
                val = d2[k]
            res[new_k] = val
    else:
        res.update(d2)

    return res


def add_new_vertices(cg, add_func_dict, add_func_io):

    #for func_name in set(add_func_dict.keys()).union(set(add_func_io.keys())):
    #    if func_name in cg.functions:
    #        raise Exception('Function {} already exists'.format(func_name))

    new_func_dict = cg.functions.copy()
    new_func_io = cg.func_io.copy()

    for func_name, func in add_func_dict.items():
        new_func_dict[func_name] = func
        new_func_io[func_name] = add_func_io[func_name]

    return CompGraph(new_func_dict, new_func_io)


def graph_union_with_suffixing(cg1, cg2, suff_1='_1', suff_2='_2', exclude=None):

    new_func_dict = merge_dicts(cg1.functions, cg2.functions, suff_1, suff_2)
    new_func_io = merge_dicts(cg1.func_io, cg2.func_io, suff_1, suff_2, rename_values=True, exclude_value_suffixing=exclude)

    return CompGraph(new_func_dict, new_func_io)


def graph_union(cg1, cg2):

    new_func_dict = merge_dicts(cg1.functions, cg2.functions)
    new_func_io = merge_dicts(cg1.func_io, cg2.func_io)

    return CompGraph(new_func_dict, new_func_io)

def create_nodes_from_comp_graph(cg):

    nodes = dict()
    for fname, f in cg.functions.items():
        nodes[fname] = Node(fname, f)

    return nodes

class UnderfinedSourceTokensException(Exception):
    pass

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

        def add_input_arg(fname, arg, token_names, edges):
            token_names.add(arg)
            edges.append((arg, fname))
            self._inputs[fname].append(arg)

        def add_output_arg(fname, arg, token_names, edges):
            token_names.add(arg)
            edges.append((fname, arg))
            self._outputs[fname].append(arg)

        token_names = set()
        edges = []
        for fname in func_io:

            if fname not in func_dict:
                raise Exception('{} is not in the set of functions'.format(fname))
            f_in, f_out = func_io[fname]

            if type(f_in) is tuple:
                for arg in f_in:
                    add_input_arg(fname, arg, token_names, edges)
            else:
                add_input_arg(fname, f_in, token_names, edges)

            if type(f_out) is tuple:
                for arg in f_out:
                    add_output_arg(fname, arg, token_names, edges)
            else:
                add_output_arg(fname, f_out, token_names, edges)

        self._G = BipartiteDigraph(fnames, token_names, edges)

    def func_inputs(self, func_name):
        return self._inputs[func_name]

    def func_outputs(self, func_name):
        return self._outputs[func_name]

    def rename_function(self, old_name, new_name):

        if old_name not in self._functions:
            raise Exception('No function with name {} exists'.format(old_name))

        if old_name != new_name:
            rename_in_dict(self._functions, old_name, new_name)
            rename_in_dict(self._func_io, old_name, new_name)

    def swap_function(self, key, new_func):

        if not key in self._functions:
            raise Exception('No function with the given key exists')

        self._functions[key] = new_func

    def to_networkx(self, func_v_attr={}, token_v_attr={}, edge_attr={}):

        default_func_v_attr = {'shape': 'rect'}
        for k in default_func_v_attr.keys():
            if k not in func_v_attr:
                func_v_attr[k] = default_func_v_attr[k]

        nxg = self._G.to_networkx(vert1_attr=func_v_attr, vert2_attr=token_v_attr, edge_attr=edge_attr)

        for fname, fobj in self.functions.items():
            if isinstance(fobj, FunctionPlaceholder):
                nxg.node[fname]['style'] = 'dashed'

        return nxg

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

        if token_name not in self._cg.source_tokens:
            raise Exception('{} is not a source token'.format(token_name))

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

        for v in self._torder:

            if v in kvargs:
                self._tm.save_payload_value(v, kvargs[v])

            elif v in self._cg.functions:

                f = self._cg.functions[v]
                f_args = (self._tm.token_value(token_name) for token_name in self._cg.func_inputs(v))
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

    def __getitem__(self, token_name):
        return self.token_value(token_name)

    @property
    def frozen_tokens(self):
        return self._frozen_tokens

    @property
    def required_source_tokens(self):
        return self._tm.free_source_tokens

    @property
    def token_manager(self):
        return self._tm
