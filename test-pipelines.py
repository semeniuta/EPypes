from __future__ import print_function

from epypes.node import Node
from epypes.pipeline import SimplePipeline, SinkPipeline, make_pipeline

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