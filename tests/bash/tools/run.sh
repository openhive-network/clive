#!/usr/bin/env bash

set -xeuo pipefail

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"



export FILE_PATH=${1:?"Missing arg #1 to specify absolute path to test"}
shift
export GENERATED_DIRECTORY_NAME=${1:?"Missing arg #2 to specify desired location generated data directory"}
shift
export BLOCK_LOG_SOURCE=${1:?"Missing arg #3 to specify block_log used to replay"}
shift
export CONFIG_INI_SOURCE=${1:?"Missing arg #4 to specify config.ini file used to run hived"}
shift


filename=$(basename -- "$FILE_PATH")
testname="${filename%_test.sh}"
generated_for_test="${GENERATED_DIRECTORY_NAME}/${testname}"
logfile="${generated_for_test}/latest.log"

export CLIVE_DATA_PATH="${generated_for_test}/.clive"
export DATADIR="${generated_for_test}/.hived"


"${SCRIPTPATH}/setup.sh" "$DATADIR" "$BLOCK_LOG_SOURCE" "$CONFIG_INI_SOURCE" 2>&1 | tee -i "$logfile"
"${FILE_PATH}" 2>&1 | tee -ia "$logfile"
"${SCRIPTPATH}/teardown.sh" "$DATADIR" 2>&1 | tee -ia "$logfile"
