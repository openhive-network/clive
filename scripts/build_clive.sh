#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")/../python"

CLIVE_DIR="${PROJECT_DIR}/clive"
DIRECT_EXECUTION="${1:-0}"
CLIVE_DEBUG="${2:-${CLIVE_DEBUG:-0}}"

if [ "${DIRECT_EXECUTION}" -eq 0 ]; then
  COMMIT_HASH=$(git rev-parse --short HEAD)
  IMAGE_BASE_NAME="clive-python-builder"
  IMAGE_NAME="${IMAGE_BASE_NAME}:${COMMIT_HASH}"

  USER_NAME=user
  USER_ID="$(id -u)"
  GROUP_ID="$(id -g)"

  echo "${PROJECT_DIR}"

  echo "Create clive python builder."
  docker build \
         -f "${PROJECT_DIR}/docker/clive-python-builder.dockerfile" \
         --build-arg USER_NAME="${USER_NAME}" \
         --build-arg USER_ID="${USER_ID}" \
         --build-arg GROUP_ID="${GROUP_ID}" \
         -t "${IMAGE_NAME}" \
         -t "${IMAGE_BASE_NAME}:devcontainer" \
         "${PROJECT_DIR}/../"

  docker run --rm \
    -v "${CLIVE_DIR}:${CLIVE_DIR}" \
    -e CLIVE_DEBUG="${CLIVE_DEBUG:-0}" \
    -w "${CLIVE_DIR}" \
    "${IMAGE_NAME}" \
    bash -c "${CLIVE_DIR}scripts/build_clive.sh 1"

else
  export POETRY_VIRTUALENVS_PATH="${PROJECT_DIR}/poetry-venv-root"

  rm -rf "${PROJECT_DIR}/setup.py"

  cd "${PROJECT_DIR}/clive"
  echo "Create proto files."
  "${PROJECT_DIR}/scripts/compile_proto.sh"

  echo "Create api files."
  poetry -C "${PROJECT_DIR}" run python3 "${PROJECT_DIR}/scripts/generate_base_client.py"

  echo "Build clive wheel package."
  poetry -C "${PROJECT_DIR}" build --format wheel

  echo "List dist directory: ${PROJECT_DIR}/dist"
  ls -lA "${PROJECT_DIR}/dist"
fi
