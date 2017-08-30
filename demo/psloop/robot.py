import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'epypes/protobuf'))

import zmq
import time
import uuid

from epypes.protobuf.event_pb2 import Event
from epypes.protobuf.timestamp_pb2 import TimeStamp, TimeStampList
from epypes.cli import parse_pubsub_args

default_pub_address = 'ipc:///tmp/psloop-vision-request'
default_sub_address = 'ipc:///tmp/psloop-vision-response'

if __name__ == '__main__':

    pub_address, sub_address = parse_pubsub_args(default_pub_address, default_sub_address)

    context = zmq.Context()

    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind(pub_address)

    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect(sub_address)
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    WAIT_BETWEEN_REQUESTS = 0.1

    while True:

        time.sleep(WAIT_BETWEEN_REQUESTS)

        t0 = time.time()

        request_id = str(uuid.uuid4())[:8]

        req_event = Event()
        req_event.type = 'VisionRequest'
        req_event.id = request_id
        timestamp = req_event.timestamps.entries.add()
        timestamp.unixtime = t0
        timestamp.description = request_id + '_t0'

        pub_socket.send(req_event.SerializeToString())
        print('Published at', pub_address)

        t1 = time.time()

        vision_response = sub_socket.recv()

        t2 = time.time()

        print('[{}] Time to get response: {} {}'.format(request_id, t2-t1, t2-t0))










