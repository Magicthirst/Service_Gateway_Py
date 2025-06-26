#!/bin/bash

PROTO_FILE="control_outlet.proto"
GENERATED_FILES=("control_outlet_pb2.py" "control_outlet_pb2_grpc.py")

if [ ! -f "$PROTO_FILE" ]; then
  echo "ERROR: file not found: $PROTO_FILE"
  exit 1
fi

for file in "${GENERATED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "ERROR: file $file does not exist. Run the generation command"
        exit 1
    fi
done

TEMP_DIR=$(mktemp -d)

if ! python3 -m grpc_tools.protoc --proto_path=. --python_out="$TEMP_DIR" --grpc_python_out="$TEMP_DIR" "$PROTO_FILE"; then
    echo "ERROR: Failed to generate gRPC code"
    rm -rf "$TEMP_DIR"
    exit 1
fi

DIFF_OUTPUT=""
for file in "${GENERATED_FILES[@]}"; do
    if ! diff -q "$file" "$TEMP_DIR/$file" > /dev/null; then
        DIFF_OUTPUT+="\n- Mismatch in $file. Regenerate the file"
    fi
done

rm -rf "$TEMP_DIR"

if [ -n "$DIFF_OUTPUT" ]; then
    echo -e "ERROR: gRPC files are not up to date\n"
    echo -e "$DIFF_OUTPUT"
    echo -e "\nRegenerate files"
    exit 1
fi

exit 0
