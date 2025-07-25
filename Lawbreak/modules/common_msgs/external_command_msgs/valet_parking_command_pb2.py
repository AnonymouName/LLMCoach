# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: modules/common_msgs/external_command_msgs/valet_parking_command.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from modules.common_msgs.basic_msgs import header_pb2 as modules_dot_common__msgs_dot_basic__msgs_dot_header__pb2
from modules.common_msgs.external_command_msgs import geometry_pb2 as modules_dot_common__msgs_dot_external__command__msgs_dot_geometry__pb2
from modules.common_msgs.external_command_msgs import lane_segment_pb2 as modules_dot_common__msgs_dot_external__command__msgs_dot_lane__segment__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='modules/common_msgs/external_command_msgs/valet_parking_command.proto',
  package='apollo.external_command',
  syntax='proto2',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\nEmodules/common_msgs/external_command_msgs/valet_parking_command.proto\x12\x17\x61pollo.external_command\x1a+modules/common_msgs/basic_msgs/header.proto\x1a\x38modules/common_msgs/external_command_msgs/geometry.proto\x1a<modules/common_msgs/external_command_msgs/lane_segment.proto\"\xb1\x02\n\x13ValetParkingCommand\x12%\n\x06header\x18\x01 \x01(\x0b\x32\x15.apollo.common.Header\x12\x16\n\ncommand_id\x18\x02 \x01(\x03:\x02-1\x12 \n\x11is_start_pose_set\x18\x03 \x01(\x08:\x05\x66\x61lse\x12\x30\n\tway_point\x18\x04 \x03(\x0b\x32\x1d.apollo.external_command.Pose\x12>\n\x10\x62lacklisted_lane\x18\x05 \x03(\x0b\x32$.apollo.external_command.LaneSegment\x12\x18\n\x10\x62lacklisted_road\x18\x06 \x03(\t\x12\x17\n\x0fparking_spot_id\x18\x07 \x02(\t\x12\x14\n\x0ctarget_speed\x18\x08 \x01(\x01'
  ,
  dependencies=[modules_dot_common__msgs_dot_basic__msgs_dot_header__pb2.DESCRIPTOR,modules_dot_common__msgs_dot_external__command__msgs_dot_geometry__pb2.DESCRIPTOR,modules_dot_common__msgs_dot_external__command__msgs_dot_lane__segment__pb2.DESCRIPTOR,])




_VALETPARKINGCOMMAND = _descriptor.Descriptor(
  name='ValetParkingCommand',
  full_name='apollo.external_command.ValetParkingCommand',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='apollo.external_command.ValetParkingCommand.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='command_id', full_name='apollo.external_command.ValetParkingCommand.command_id', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=True, default_value=-1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='is_start_pose_set', full_name='apollo.external_command.ValetParkingCommand.is_start_pose_set', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='way_point', full_name='apollo.external_command.ValetParkingCommand.way_point', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='blacklisted_lane', full_name='apollo.external_command.ValetParkingCommand.blacklisted_lane', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='blacklisted_road', full_name='apollo.external_command.ValetParkingCommand.blacklisted_road', index=5,
      number=6, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='parking_spot_id', full_name='apollo.external_command.ValetParkingCommand.parking_spot_id', index=6,
      number=7, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='target_speed', full_name='apollo.external_command.ValetParkingCommand.target_speed', index=7,
      number=8, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
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
  serialized_start=264,
  serialized_end=569,
)

_VALETPARKINGCOMMAND.fields_by_name['header'].message_type = modules_dot_common__msgs_dot_basic__msgs_dot_header__pb2._HEADER
_VALETPARKINGCOMMAND.fields_by_name['way_point'].message_type = modules_dot_common__msgs_dot_external__command__msgs_dot_geometry__pb2._POSE
_VALETPARKINGCOMMAND.fields_by_name['blacklisted_lane'].message_type = modules_dot_common__msgs_dot_external__command__msgs_dot_lane__segment__pb2._LANESEGMENT
DESCRIPTOR.message_types_by_name['ValetParkingCommand'] = _VALETPARKINGCOMMAND
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ValetParkingCommand = _reflection.GeneratedProtocolMessageType('ValetParkingCommand', (_message.Message,), {
  'DESCRIPTOR' : _VALETPARKINGCOMMAND,
  '__module__' : 'modules.common_msgs.external_command_msgs.valet_parking_command_pb2'
  # @@protoc_insertion_point(class_scope:apollo.external_command.ValetParkingCommand)
  })
_sym_db.RegisterMessage(ValetParkingCommand)


# @@protoc_insertion_point(module_scope)
