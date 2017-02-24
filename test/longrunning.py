from __future__ import print_function

from threading import Thread
import time
import multiprocessing as mp

from epypes.pipeline import Pipeline, SinkPipeline
from epypes.node import Node

def lrf(token, sleep_time=10):
    print(time.strftime('%H:%M:%S'), 'started with', token)
    time.sleep(sleep_time)
    print(time.strftime('%H:%M:%S'), 'finished')

class LongRunningPipeline(SinkPipeline):
    def __init__(self, q_in):
        name = self.__class__.__name__
        nodes = [Node('LRF', lrf, sleep_time=10)]
        SinkPipeline.__init__(self, name, nodes, q_in)

if __name__ == '__main__':

    qin = mp.Queue()
    p = LongRunningPipeline(qin)
    p.listen()

    qin.put('QUEUE-EVENT')

    #p.modify_node_argument('LRF', 'sleep_time', 1)
    #p.run('PIPE-RUN')


    #p.request_stop()
