#!/bin/bash

set -euo pipefail

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit 1; pwd -P )"

IMAGE_NAME=${1:?"Missing arg #1 to specify built docker image name"}

ESCAPED_IMAGE_NAME=${IMAGE_NAME//\//\\/}

cp -f "${SCRIPTPATH}/../start_clive.sh.template" "${SCRIPTPATH}/../start_clive.sh"
sed -i -e "s/<IMG_PLACEHOLDER>/${ESCAPED_IMAGE_NAME}/g" "${SCRIPTPATH}/../start_clive.sh"
