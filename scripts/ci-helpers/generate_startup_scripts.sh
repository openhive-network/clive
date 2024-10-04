#!/bin/bash

set -euo pipefail

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit 1; pwd -P )"

IMAGE_NAME=${1:?"Missing arg #1 to specify built docker image name"}

ESCAPED_IMAGE_NAME=${IMAGE_NAME//\//\\/}

cp -f "${SCRIPTPATH}/../templates/base.sh.template" "${SCRIPTPATH}/../templates/base.sh"
sed -i -e "s/<IMG_PLACEHOLDER>/${ESCAPED_IMAGE_NAME}/g" "${SCRIPTPATH}/../templates/base.sh"

template_files=("start_clive.sh.template" "start_clive_cli.sh.template")
for template_file in "${template_files[@]}"; do
  file="${template_file%.template}"
  sed "/BASE_PLACEHOLDER/{r ${SCRIPTPATH}/../templates/base.sh
  d}" "${SCRIPTPATH}/../templates/${template_file}" > "${SCRIPTPATH}/../${file}"
  chmod +x "${SCRIPTPATH}/../${file}"
done
