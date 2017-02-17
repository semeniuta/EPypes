from threading import Thread

class PipelineService(Thread):

    def __init__(self, pipe):
        self._pipe = pipe
