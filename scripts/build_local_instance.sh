#! /bin/bash
set -euo pipefail

SCRIPTSDIR="$(
  cd -- "$(dirname "$0")" >/dev/null 2>&1
  pwd -P
)"

IMAGE_TAG="local"
SRC_DIR="${SCRIPTSDIR}/../"
REGISTRY_URL="registry.gitlab.syncad.com/hive/clive"

# EDIT THESE VARIABLES
#    IMAGE could be get from prepare_hived_image job like: https://gitlab.syncad.com/hive/clive/-/jobs/787089#L342
IMAGE="registry.gitlab.syncad.com/hive/hive/testnet-base_instance:testnet-base_instance-8233eeb01b15b2ea557e7a6d5c81f9e81b996b75"
CLIVE_VERSION="1.27.5.2"
BUILD_TESTNET=1

HIVED_SOURCE_IMAGE="${IMAGE}"
BASE_IMAGE="mwalbeck/python-poetry:1.7-3.10"

BUILD_INSTANCE_PATH=$(realpath "${SCRIPTSDIR}/ci-helpers/")
cd "${BUILD_INSTANCE_PATH}"

# Variables in scripts should be double-quoted to prevent globbing and splitting.
# See https://www.shellcheck.net/wiki/SC2086 for more info.

BUILD_ARGS=(
  "${IMAGE_TAG}"
  "${SRC_DIR}"
  "${REGISTRY_URL}"
  "--hived-source-image=${HIVED_SOURCE_IMAGE}"
  "--base-image=${BASE_IMAGE}"
  "--clive-version=${CLIVE_VERSION}"
)

if [ ${BUILD_TESTNET} -eq 1 ]; then
  BUILD_ARGS+=(--embedded-testnet)
fi

./build_instance.sh "${BUILD_ARGS[@]}"
