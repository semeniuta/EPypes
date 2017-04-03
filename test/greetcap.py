from __future__ import print_function

import multiprocessing as mp

from epypes.dag import ComputationalGraph
from epypes.pipeline import Pipeline, SourcePipeline, SinkPipeline

def say_hello(to_whom, exclamation=False):
    s = 'Hello ' + to_whom
    if exclamation:
        s += '!'
    return s

def capitalize(s):
    return s.upper()

def dispatch_greet(event_str):
    return {'input_string': event_str['capitalized_string']}

if __name__ == '__main__':

    greet_cg = ComputationalGraph(

        func_dict={
            'greet': say_hello,
            'capitalize': capitalize
        },

        func_io={
            'greet': (('name', 'exclamation'), 'hello_string'),
            'capitalize': ('hello_string', 'capitalized_string')
        }
    )

    print_cg = ComputationalGraph(
        func_dict={'print': print},
        func_io={'print': ('input_string', None)}
    )

    q = mp.Queue()

    greet_pipe = SourcePipeline('Greeter', greet_cg, q_out=q, frozen_tokens={'exclamation': True})

    print_pipe = SinkPipeline('Printer', print_cg, q_in=q, event_dispatcher=dispatch_greet)

    print_pipe.listen()

    greet_pipe.run(name='Alex', tokens_to_get=('capitalized_string',))

