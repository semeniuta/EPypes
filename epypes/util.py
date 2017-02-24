import multiprocessing as mp
import uuid

from epypes import pipeline

def make_full_pipeline(pipe, queues=()):

    if queues == ():
        qin = mp.Queue()
        qout = mp.Queue()
    else:
        qin, qout = queues

    pipe = pipeline.FullPipeline(pipe.name, pipe.nodes, qin, qout)

    return pipe, qin, qout

def create_name_with_uuid(TargetClass):
    return TargetClass.__name__ + str(uuid.uuid4())[:8]

def create_basic_queue():
    import sys
    ver = sys.version_info[:2]
    if ver[0] == 2:
        import Queue as queue
    else:
        import queue
    return queue.Queue()