#!/usr/bin/env bash

set -xeuo pipefail

export DATADIR=${1:?"Missing arg #1 to specify desired location if hived data directory"}
shift

PID=$(< "$DATADIR/hived.pid")
echo "hived pid: $PID"
kill $PID
tail --pid="$PID" -f /dev/null
