"""
Test compisition of a SourcePipeline with a SinkPipeline
havign a common queue
"""

from epypes.queue import Queue
from epypes.compgraph import CompGraph
from epypes.pipeline import Pipeline, SourcePipeline, SinkPipeline


def say_hello(to_whom, exclamation=False):
    s = 'Hello ' + to_whom
    if exclamation:
        s += '!'
    return s


def capitalize(s):
    return s.upper()


def greet_out(pipe):
    return pipe['capitalized_string']


def dispatch_greet(e):
    return {'input_string': e}


def test_pipelines_composition_with_q(capfd):

    greet_cg = CompGraph(

        func_dict={
            'greet': say_hello,
            'capitalize': capitalize
        },

        func_io={
            'greet': (('name', 'exclamation'), 'hello_string'),
            'capitalize': ('hello_string', 'capitalized_string')
        }
    )

    print_cg = CompGraph(
        func_dict={'print': print},
        func_io={'print': ('input_string', None)}
    )

    q = Queue()

    ft = {'exclamation': True}
    greet_pipe = SourcePipeline('Greeter', greet_cg, q_out=q, out_prep_func=greet_out, frozen_tokens=ft)

    print_pipe = SinkPipeline('Printer', print_cg, q_in=q, event_dispatcher=dispatch_greet)

    print_pipe.listen()

    greet_pipe.run(name='Alex')

    greet_pipe.stop()
    print_pipe.stop()

    out, err = capfd.readouterr()
    assert out.split('\n')[0] == "HELLO ALEX!"

