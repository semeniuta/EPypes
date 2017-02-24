import time
import threading
import multiprocessing as mp
from epypes.pipeline import Node, Pipeline, SinkPipeline, make_full_pipeline

def say_hello(to_whom, exclamation=False):
    s = 'Hello ' + to_whom
    if exclamation:
        s += '!'
    return s

def test():
    g = Node('Greeter', say_hello, exclamation=False)
    p = Node('Capitalizer', lambda x: x.upper())

    spipe = Pipeline('MyPipe', [g, p])
    pipe, qin, qout = make_full_pipeline(spipe)

    print_node = Node('Printer', lambda x: print(x))
    pipe_out = SinkPipeline('PrinterPipe', [print_node], qout)

    pipe.listen()
    pipe_out.listen()

    qin.put('')
    time.sleep(0.05)

    pipe.request_stop()
    pipe_out.request_stop()

if __name__ == '__main__':
    for i in range(100):
        print(i)
        test()
