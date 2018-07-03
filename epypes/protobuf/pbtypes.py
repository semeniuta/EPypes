"""
A single entry point for all EPypes' Protobuf types
"""

import os
import sys


def enable_protobuf_types():

    EPYPES_PROTOBUF_PATH = os.path.dirname(__file__)
    sys.path.append(EPYPES_PROTOBUF_PATH)


enable_protobuf_types()

# Attribute, AttributeList
from epypes.protobuf import attributes_pb2
Attribute = attributes_pb2.Attribute
AttributeList = attributes_pb2.AttributeList

# Event
from epypes.protobuf import event_pb2
Event = event_pb2.Event

# Image
from epypes.protobuf import image_pb2
Image = image_pb2.Image

# ImagePair
from epypes.protobuf import imagepair_pb2
ImagePair = imagepair_pb2.ImagePair

# JustBytes
from epypes.protobuf import justbytes_pb2
JustBytes = justbytes_pb2.JustBytes

# TimeStamp, TimeStampList
from epypes.protobuf import timestamp_pb2
TimeStamp = timestamp_pb2.TimeStamp
TimeStampList = timestamp_pb2.TimeStampList
