#! /bin/bash
set -euo pipefail

SCRIPTSDIR="$(
  cd -- "$(dirname "$0")" >/dev/null 2>&1
  pwd -P
)"

IMAGE_TAG="local"
SRC_DIR="${SCRIPTSDIR}/../"
REGISTRY_URL="registry.gitlab.syncad.com/hive/clive"

# >>> EDIT THESE VARIABLES

#    Depends if building testnet. HIVED_SOURCE_IMAGE could be get from prepare_mainnet_hived_image or prepare_testnet_hived_image job like: https://gitlab.syncad.com/hive/clive/-/jobs/2300417#L195
HIVED_SOURCE_IMAGE="registry.gitlab.syncad.com/hive/hive/testnet:42d81955"

#    PYTHON_INSTALLER_IMAGE is the image that will be used for installing the python application
PYTHON_INSTALLER_IMAGE="registry.gitlab.syncad.com/hive/common-ci-configuration/python_development@sha256:cf7cc40b911d2baec112ffab85d80748034239aac9b11e06064a79f0221ad258"

#     Depends if building testnet. BASE_IMAGE is the image on which clive image will be built.
BASE_IMAGE="registry.gitlab.syncad.com/hive/common-ci-configuration/python_development@sha256:cf7cc40b911d2baec112ffab85d80748034239aac9b11e06064a79f0221ad258"

#   CLIVE_VERSION is the version of clive which will be available in the image, Clive won't be built from sources but .whl file will be used to install it.
CLIVE_VERSION="1.28.1.1"

BUILD_TESTNET=1
# <<<

BUILD_INSTANCE_PATH=$(realpath "${SCRIPTSDIR}/ci-helpers/")
cd "${BUILD_INSTANCE_PATH}"

BUILD_ARGS=(
  "${IMAGE_TAG}"
  "${SRC_DIR}"
  "${REGISTRY_URL}"
  "--hived-source-image=${HIVED_SOURCE_IMAGE}"
  "--python-installer-image=${PYTHON_INSTALLER_IMAGE}"
  "--base-image=${BASE_IMAGE}"
  "--clive-version=${CLIVE_VERSION}"
)

if [ ${BUILD_TESTNET} -eq 1 ]; then
  BUILD_ARGS+=(--embedded-testnet)
fi

./build_instance.sh "${BUILD_ARGS[@]}"
