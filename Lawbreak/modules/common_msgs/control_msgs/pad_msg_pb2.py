# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: modules/common_msgs/control_msgs/pad_msg.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from modules.common_msgs.basic_msgs import header_pb2 as modules_dot_common__msgs_dot_basic__msgs_dot_header__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='modules/common_msgs/control_msgs/pad_msg.proto',
  package='apollo.control',
  syntax='proto2',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n.modules/common_msgs/control_msgs/pad_msg.proto\x12\x0e\x61pollo.control\x1a+modules/common_msgs/basic_msgs/header.proto\"b\n\nPadMessage\x12%\n\x06header\x18\x01 \x01(\x0b\x32\x15.apollo.common.Header\x12-\n\x06\x61\x63tion\x18\x02 \x01(\x0e\x32\x1d.apollo.control.DrivingAction*2\n\rDrivingAction\x12\t\n\x05START\x10\x01\x12\t\n\x05RESET\x10\x02\x12\x0b\n\x07VIN_REQ\x10\x03'
  ,
  dependencies=[modules_dot_common__msgs_dot_basic__msgs_dot_header__pb2.DESCRIPTOR,])

_DRIVINGACTION = _descriptor.EnumDescriptor(
  name='DrivingAction',
  full_name='apollo.control.DrivingAction',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='START', index=0, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='RESET', index=1, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='VIN_REQ', index=2, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=211,
  serialized_end=261,
)
_sym_db.RegisterEnumDescriptor(_DRIVINGACTION)

DrivingAction = enum_type_wrapper.EnumTypeWrapper(_DRIVINGACTION)
START = 1
RESET = 2
VIN_REQ = 3



_PADMESSAGE = _descriptor.Descriptor(
  name='PadMessage',
  full_name='apollo.control.PadMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='apollo.control.PadMessage.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='action', full_name='apollo.control.PadMessage.action', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=111,
  serialized_end=209,
)

_PADMESSAGE.fields_by_name['header'].message_type = modules_dot_common__msgs_dot_basic__msgs_dot_header__pb2._HEADER
_PADMESSAGE.fields_by_name['action'].enum_type = _DRIVINGACTION
DESCRIPTOR.message_types_by_name['PadMessage'] = _PADMESSAGE
DESCRIPTOR.enum_types_by_name['DrivingAction'] = _DRIVINGACTION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

PadMessage = _reflection.GeneratedProtocolMessageType('PadMessage', (_message.Message,), {
  'DESCRIPTOR' : _PADMESSAGE,
  '__module__' : 'modules.common_msgs.control_msgs.pad_msg_pb2'
  # @@protoc_insertion_point(class_scope:apollo.control.PadMessage)
  })
_sym_db.RegisterMessage(PadMessage)


# @@protoc_insertion_point(module_scope)
