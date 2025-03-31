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

#    HIVED_SOURCE_IMAGE could be get from prepare_mainnet_hived_image or prepare_testnet_hived_image job like: https://gitlab.syncad.com/hive/clive/-/jobs/787089#L342 Depends if building testnet - can be base_instance or testnet-base_instance
HIVED_SOURCE_IMAGE="registry.gitlab.syncad.com/hive/hive/testnet-base_instance:8a42333b"

#    BASE_IMAGE is the image on which clive image will be built. Depends if building testnet - can be either https://gitlab.syncad.com/hive/clive/container_registry/682 or https://gitlab.syncad.com/hive/clive/container_registry/684
BASE_IMAGE="registry.gitlab.syncad.com/hive/clive/clive-testnet-base-image@sha256:d38883407b5860a89e7491b1de4153c516dc5ae87ca9988fba0ed0400e97f98f"

#   CLIVE_VERSION is the version of clive which will be available in the image, Clive won't be built from sources but .whl file will be used to install it.
CLIVE_VERSION="1.27.5.21"

BUILD_TESTNET=1
# <<<

BUILD_INSTANCE_PATH=$(realpath "${SCRIPTSDIR}/ci-helpers/")
cd "${BUILD_INSTANCE_PATH}"

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
