import uuid


def generate_short_uuid():
    return str(uuid.uuid4())[:8]


def create_name_with_uuid(TargetClass):
    return TargetClass.__name__ + generate_short_uuid()


def create_basic_queue():
    import sys
    ver = sys.version_info[:2]
    if ver[0] == 2:
        import Queue as queue
    else:
        import queue
    return queue.Queue()
