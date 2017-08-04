import sys
import numpy as np
from queue import Queue

from epypes.compgraph import CompGraph
from epypes.pipeline import Pipeline, SinkPipeline
from epypes.zeromq import ZeroMQSubscriber

def parse_int_from_bytes_string(s):

    try:
        num = int(s)
        return num
    except ValueError:
        return 0

def create_random_vector(sz):
    return np.random.rand(sz)

def print_res(num, vec):
    print('{0} -> {1}'.format(num, vec))


if __name__ == '__main__':

    cg = CompGraph(

        func_dict = {
            'parse_int': parse_int_from_bytes_string,
            'make_vec': create_random_vector,
            'print_vec': print_res
        },

        func_io = {
            'parse_int': ('s_bytes', 'vec_size'),
            'make_vec': ('vec_size', 'vector'),
            'print_vec': (('vec_size', 'vector'), None)
        }
    )

    def dispatch_event(e):
        return {'s_bytes': e}

    q = Queue()

    default_address = 'ipc:///tmp/epypeszmq-testpub'

    if len(sys.argv) == 1:
        address = default_address
    else:
        address = sys.argv[1]

    pipe = SinkPipeline('make_vector', cg, q, event_dispatcher=dispatch_event)
    sub = ZeroMQSubscriber(address, q)

    def stop():
        sub.stop()
        pipe.stop()

    pipe.listen()
    sub.start()

