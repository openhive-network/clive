#!/usr/bin/env bash

set -xeuo pipefail

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"


trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT


GENERATED_DIRECTORY_NAME="${SCRIPTPATH}/generated"
rm "$GENERATED_DIRECTORY_NAME" -rf && mkdir "$GENERATED_DIRECTORY_NAME"


# check for beekeeper and hived binaries
"$CLIVE_BEEKEEPER__PATH" --version >> /dev/null
"$HIVED_PATH" --version | grep testnet >> /dev/null

export CLIVE_SECRETS__DEFAULT_KEY="5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYik"
export CLIVE_SECRETS__NODE_ADDRESS="http://127.0.0.1:8090"
export CLIVE_NODE__CHAIN_ID="18dcf0a285365fc58b71f18b3d3fec954aa0c141c44e4e5cb4cf777b9eab274e"
export BLOCK_LOG_SOURCE="${SCRIPTPATH}/../clive-local-tools/clive_local_tools/testnet_block_log/blockchain/block_log"
export CONFIG_INI_SOURCE="${SCRIPTPATH}/../clive-local-tools/clive_local_tools/testnet_block_log/config.ini"


find "$SCRIPTPATH" -regex ".*_test.sh" -exec \
  "${SCRIPTPATH}/tools/run.sh" {} "$GENERATED_DIRECTORY_NAME" "$BLOCK_LOG_SOURCE" "$CONFIG_INI_SOURCE" \;



# find  -regex ".*_test.sh" -print0 | while read -d $'\0' file_relative_path
# do

#   filename=$(basename -- "$file_relative_path")
#   testname="${filename%_test.sh}"
#   generated_for_test="${GENERATED_DIRECTORY_NAME}/${testname}"
#   logfile="${generated_for_test}/latest.log"
#   export CLIVE_DATA_PATH="${generated_for_test}/.clive"
#   export DATADIR="${generated_for_test}/.hived"
#   echo "executing $testname"

#   "${SCRIPTPATH}/tools/setup.sh" "$DATADIR" "$BLOCK_LOG_SOURCE" "$CONFIG_INI_SOURCE" 2>&1 
#   "${SCRIPTPATH}/${file_relative_path}" 2>&1 
#   "${SCRIPTPATH}/tools/teardown.sh" "$DATADIR" 2>&1

# done
