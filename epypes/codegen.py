from io import StringIO

from epypes.graph import DepthFirstOrder
from epypes.compgraph import TokenManager

INDENT = ' ' * 4

def format_args(*args):

    n = len(args)
    template = (n * '{}, ')[:-2]
    return template.format(*args)


def format_kwargs(**kwargs):

    out = StringIO()
    for k, v in kwargs.items():
        out.write('{}={}, '.format(k, v))

    return out.getvalue()[:-2]


def generate_code_from_compgraph(name, cg, frozen_tokens, return_tokens):

    assert set(frozen_tokens).issubset(cg.source_tokens)
    assert set(return_tokens).issubset(cg.tokens)

    free_src_tokens = cg.source_tokens.difference(frozen_tokens)

    out = StringIO()

    args_str = format_args(*list(free_src_tokens))
    kwargs_str = format_kwargs(**frozen_tokens)
    out.write('def {}({}, {}):\n\n'.format(name, args_str, kwargs_str))

    torder = DepthFirstOrder(cg.graph).topological_order
    torder_functions = list(filter(lambda x: x in cg.functions, torder))

    for func_name in torder_functions:

        f_callable = cg.functions[func_name]
        f_args = cg.func_inputs(func_name)
        f_outputs = cg.func_outputs(func_name)

        f_args_str = format_args(*f_args)
        f_call_str = '{}({})\n'.format(f_callable.__name__, f_args_str)

        if len(f_outputs) == 1:
            var_str = f_outputs[0]

        elif len(f_outputs) > 1:
            var_str = 'res_{}'.format(func_name)

        else:
            var_str = ''

        out.write(INDENT)
        out.write('{} = '.format(var_str))
        out.write(f_call_str)

        if len(f_outputs) > 1:

            eq_last_out = ' = {}\n'.format(var_str)
            unpack_str = format_args(*f_outputs) + eq_last_out

            out.write(INDENT)
            out.write(unpack_str)

        out.write('\n')

    ret_vars_str = format_args(*return_tokens)
    out.write('return {}\n'.format(ret_vars_str))

    return out.getvalue()

