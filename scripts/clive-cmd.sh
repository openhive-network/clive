#!/bin/bash

# Exit immediately on error, unset variables are errors, and fail on any command in a pipeline
set -euo pipefail

# shellcheck disable=SC1091
source "${PYTHON_VENV_PATH}/bin/activate"
# shellcheck disable=SC1091
source /clive/session.env

_TST1=${CLIVE_BEEKEEPER__SESSION_TOKEN:?"Missing critical session variable #1"}
_TST2=${CLIVE_BEEKEEPER__REMOTE_ADDRESS:?"Missing critical session variable #2"}

export CLIVE_BEEKEEPER__SESSION_TOKEN
export CLIVE_BEEKEEPER__REMOTE_ADDRESS

cd /clive

clive "$@"
