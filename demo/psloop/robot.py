import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'epypes/protobuf'))

import zmq
import time
import uuid
import pandas as pd

from epypes.protobuf.event_pb2 import Event
from epypes.protobuf.justbytes_pb2 import JustBytes
from epypes.protobuf.pbprocess import add_attribute, get_attributes_dict
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

    N_REQUESTS = 50

    all_attr_dicts = []

    time.sleep(1) # <- somehow the first request gets lost w/o this waiting in the beginning

    for req_attempt_i in range(N_REQUESTS):

        t0 = time.time()

        request_id = str(uuid.uuid4())[:8]

        req_event = Event()
        req_event.type = 'VisionRequest'
        req_event.id = request_id
        add_attribute(req_event, 'time_vision_request', t0)

        pub_socket.send(req_event.SerializeToString())
        print('Published at', pub_address)

        t1 = time.time()

        response_data = sub_socket.recv()

        t2 = time.time()

        vision_response = JustBytes()
        vision_response.ParseFromString(response_data)
        attr_dict = get_attributes_dict(vision_response.attributes.entries)

        #overhead = trip_duration - attr_dict['time_processing']
        #attr_dict['trip_duration'] = t2 - attr_dict['time_vision_request']

        attr_dict['time_got_vision_response'] = t2
        all_attr_dicts.append(attr_dict)

        time.sleep(WAIT_BETWEEN_REQUESTS)

    df = pd.DataFrame(all_attr_dicts)
    df.to_csv('experiment.csv')










