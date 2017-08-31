import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'epypes/protobuf'))

import zmq
import time
import uuid

from epypes.protobuf.event_pb2 import Event
from epypes.protobuf.justbytes_pb2 import JustBytes
from epypes.protobuf.pbprocess import add_timestamp, timestamp_entries_to_dict
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

    time.sleep(1)
    while True:

        t0 = time.time()

        request_id = str(uuid.uuid4())[:8]

        req_event = Event()
        req_event.type = 'VisionRequest'
        req_event.id = request_id
        add_timestamp(req_event, t0, description='time_vision_request')

        pub_socket.send(req_event.SerializeToString())
        print('Published at', pub_address)

        t1 = time.time()

        response_data = sub_socket.recv()

        t2 = time.time()

        #print('[{}] Time to get response: {} {}'.format(request_id, t2-t1, t2-t0))

        vision_response = JustBytes()
        vision_response.ParseFromString(response_data)
        ts_dict = timestamp_entries_to_dict(vision_response.timestamps.entries)
        print(ts_dict['time_got_images'] - ts_dict['time_vision_request'])

        time.sleep(WAIT_BETWEEN_REQUESTS)










