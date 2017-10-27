# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: attributes.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='attributes.proto',
  package='',
  syntax='proto2',
  serialized_pb=_b('\n\x10\x61ttributes.proto\"\x96\x01\n\tAttribute\x12\x1d\n\x04type\x18\x01 \x02(\x0e\x32\x0f.Attribute.Type\x12\x0b\n\x03key\x18\x02 \x02(\t\x12\x0f\n\x07str_val\x18\x03 \x01(\t\x12\x12\n\ndouble_val\x18\x04 \x01(\x01\x12\x0f\n\x07int_val\x18\x05 \x01(\x05\"\'\n\x04Type\x12\n\n\x06STRING\x10\x01\x12\n\n\x06\x44OUBLE\x10\x02\x12\x07\n\x03INT\x10\x03\",\n\rAttributeList\x12\x1b\n\x07\x65ntries\x18\x01 \x03(\x0b\x32\n.Attribute')
)



_ATTRIBUTE_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='Attribute.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STRING', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DOUBLE', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INT', index=2, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=132,
  serialized_end=171,
)
_sym_db.RegisterEnumDescriptor(_ATTRIBUTE_TYPE)


_ATTRIBUTE = _descriptor.Descriptor(
  name='Attribute',
  full_name='Attribute',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='Attribute.type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='key', full_name='Attribute.key', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='str_val', full_name='Attribute.str_val', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='double_val', full_name='Attribute.double_val', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='int_val', full_name='Attribute.int_val', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _ATTRIBUTE_TYPE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=21,
  serialized_end=171,
)


_ATTRIBUTELIST = _descriptor.Descriptor(
  name='AttributeList',
  full_name='AttributeList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='entries', full_name='AttributeList.entries', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=173,
  serialized_end=217,
)

_ATTRIBUTE.fields_by_name['type'].enum_type = _ATTRIBUTE_TYPE
_ATTRIBUTE_TYPE.containing_type = _ATTRIBUTE
_ATTRIBUTELIST.fields_by_name['entries'].message_type = _ATTRIBUTE
DESCRIPTOR.message_types_by_name['Attribute'] = _ATTRIBUTE
DESCRIPTOR.message_types_by_name['AttributeList'] = _ATTRIBUTELIST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Attribute = _reflection.GeneratedProtocolMessageType('Attribute', (_message.Message,), dict(
  DESCRIPTOR = _ATTRIBUTE,
  __module__ = 'attributes_pb2'
  # @@protoc_insertion_point(class_scope:Attribute)
  ))
_sym_db.RegisterMessage(Attribute)

AttributeList = _reflection.GeneratedProtocolMessageType('AttributeList', (_message.Message,), dict(
  DESCRIPTOR = _ATTRIBUTELIST,
  __module__ = 'attributes_pb2'
  # @@protoc_insertion_point(class_scope:AttributeList)
  ))
_sym_db.RegisterMessage(AttributeList)


# @@protoc_insertion_point(module_scope)