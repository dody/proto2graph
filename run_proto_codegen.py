#!/opt/python-2.7/bin/python2.7
"""Runs protoc with the gRPC plugin to generate messages and gRPC stubs."""
import sys

from grpc.tools import protoc

# google/protobuf/descriptor.proto: File not found.
# proto_imports=".:${GOPATH}/src/github.com/google/protobuf/src:${GOPATH}/src"

# h:\protos\venv\lib\python2.7\site-packages\grpc_tools\_proto\google\protobuf\


proto_name = "cert.proto"
try:
    proto_name=sys.argv[1]
except IndexError:
    print('Usage: run_proto_codegen.py <proto_filename>')

if proto_name is not None:
    protoc.main(
        (
        '',
        '-I.',
        '--python_out=.',
        '--grpc_python_out=.',
        proto_name,
        )
    )
