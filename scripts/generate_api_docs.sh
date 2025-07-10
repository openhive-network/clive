#!/bin/bash
set -e

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
PROJECT_DIR="${SCRIPTPATH}/.."

REPO_URL="${1:?Missing repository URL}"
REVISION_INFO="${2:?Missing revision info}"
DOCUMENTATION_URL="${3}"
OUTPUT_DIR="${4:-docs/api}"

MODULE_NAME="clive"

pushd "${PROJECT_DIR}"

mkdir -vp "${OUTPUT_DIR}"

# Generate docs
pdoc "${MODULE_NAME}" \
  --output-dir "${OUTPUT_DIR}" \
  --force \
  --html \
  --logo "${DOCUMENTATION_URL}" \
  --footer-text "Clive API docs @ ${REVISION_INFO}" \
  --source-link-format "${REPO_URL}/-/blob/${REVISION_INFO}/{module}.py#L{lineno}"

if [[ -n "${DOCUMENTATION_URL}" ]]; then
  echo "Attempting to replace generated documentation URL placeholder: ${DOCUMENTATION_URL}"
  sed -i "s<\${GEN_DOC_URL}<${DOCUMENTATION_URL}<g" README.md
fi

popd
