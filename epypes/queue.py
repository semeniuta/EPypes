import sys

ver = sys.version_info[:2]
if ver[0] == 2:
    import Queue as py2_queue
    Queue = py2_queue.Queue
else:
    import queue as py3_queue
    Queue = py3_queue.Queue


def create_queue_putter(func, q_out):

    def closure(event):
        res = func(event)
        q_out.put(res)

    return closure
