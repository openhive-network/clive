#!/usr/bin/env bash

set -xeuo pipefail

export DATADIR=${1:?"Missing arg #1 to specify desired location if hived data directory"}
shift

export BLOCK_LOG_SOURCE=${1:?"Missing arg #2 to specify block_log used to replay"}
shift

export CONFIG_INI_SOURCE=${1:?"Missing arg #3 to specify config.ini file used to run hived"}
shift

mkdir -p "$DATADIR"
mkdir -p "${DATADIR}/blockchain"
cp "$BLOCK_LOG_SOURCE" "${DATADIR}/blockchain/block_log"
cp "$CONFIG_INI_SOURCE" "${DATADIR}/config.ini"

# start testnet node instance
"$HIVED_PATH" --webserver-http-endpoint=0.0.0.0:8090 --data-dir="$DATADIR" --replay >> "$DATADIR/hived.log" 2>&1 &

echo "$!" >> "$DATADIR/hived.pid"

# credits: https://stackoverflow.com/a/39028690/11738218
RETRIES=12
until curl -I http://127.0.0.1:8090 2>&1 || [ $RETRIES -eq 0 ]; do
  echo "Waiting for hived http server, $((RETRIES--)) remaining attempts..."
  sleep 10
done
curl -I http://127.0.0.1:8090 2>&1
