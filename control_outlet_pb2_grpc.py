# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import control_outlet_pb2 as control__outlet__pb2

GRPC_GENERATED_VERSION = '1.73.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in control_outlet_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class SyncControlOutletStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Launch = channel.unary_unary(
                '/Syncing_Battleship.SyncControlOutlet/Launch',
                request_serializer=control__outlet__pb2.SessionLaunchInfo.SerializeToString,
                response_deserializer=control__outlet__pb2.NewSessionInfo.FromString,
                _registered_method=True)
        self.Welcome = channel.unary_unary(
                '/Syncing_Battleship.SyncControlOutlet/Welcome',
                request_serializer=control__outlet__pb2.WelcomeRequest.SerializeToString,
                response_deserializer=control__outlet__pb2.WelcomeResponse.FromString,
                _registered_method=True)


class SyncControlOutletServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Launch(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Welcome(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SyncControlOutletServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Launch': grpc.unary_unary_rpc_method_handler(
                    servicer.Launch,
                    request_deserializer=control__outlet__pb2.SessionLaunchInfo.FromString,
                    response_serializer=control__outlet__pb2.NewSessionInfo.SerializeToString,
            ),
            'Welcome': grpc.unary_unary_rpc_method_handler(
                    servicer.Welcome,
                    request_deserializer=control__outlet__pb2.WelcomeRequest.FromString,
                    response_serializer=control__outlet__pb2.WelcomeResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Syncing_Battleship.SyncControlOutlet', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('Syncing_Battleship.SyncControlOutlet', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class SyncControlOutlet(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Launch(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Syncing_Battleship.SyncControlOutlet/Launch',
            control__outlet__pb2.SessionLaunchInfo.SerializeToString,
            control__outlet__pb2.NewSessionInfo.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Welcome(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Syncing_Battleship.SyncControlOutlet/Welcome',
            control__outlet__pb2.WelcomeRequest.SerializeToString,
            control__outlet__pb2.WelcomeResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
