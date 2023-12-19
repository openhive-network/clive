#!/usr/bin/env bash

set -xeuo pipefail

PID=$(< "$DATADIR/hived.pid")
echo "hived pid: $PID"
kill $PID
