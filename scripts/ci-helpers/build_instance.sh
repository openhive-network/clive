#! /bin/bash
set -euo pipefail

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
SCRIPTSDIR="$SCRIPTPATH/.."

LOG_FILE=build_instance.log
source "$SCRIPTSDIR/common.sh"

BUILD_IMAGE_TAG=""
REGISTRY=""
SRCROOTDIR=""

IMAGE_TAG_PREFIX=""
IMAGE_TAG_CLI=""
IMAGE_PATH_SUFFIX=""

BEEKEEPER_IMAGE=""
BASE_IMAGE=""

DOCKER_TARGET="instance"

INTERACTIVE_CLI_MODE=0

print_help () {
    echo "Usage: $0 <image_tag> <src_dir> <registry_url> [OPTION[=VALUE]]..."
    echo
    echo "Allows to build docker image containing clive installation"
    echo "OPTIONS:"
    echo "  --beekeeper-source-image=image_name Allows to specify image name containing a prebuilt beekeper tool"
    echo "  --base-image=image_name             Allows to specify an image name being use as a base of the one to be built"
    echo "  --embedded-testnet                  Allows to build a clive image having embedded a hived testnet inside (ready for immediate sanboxing run)"
    echo "  --interactive-cli                   Allows to build a clive image having interactive CLI mode ready to use"
    echo "  --image-path-suffix                 Allows to specify a suffix to be added to the image path, to organize images in a more structured directory-like way"
    echo "  --help                              Display this help screen and exit"
    echo
}

EXPORT_PATH=""

while [ $# -gt 0 ]; do
  case "$1" in
    --beekeeper-source-image=*)
      BEEKEEPER_IMAGE="${1#*=}"
      ;;
    --base-image=*)
      BASE_IMAGE="${1#*=}"
      ;;
    --embedded-testnet)
      DOCKER_TARGET="embedded_testnet_instance"
      IMAGE_TAG_PREFIX="testnet-"
      ;;
    --interactive-cli)
      INTERACTIVE_CLI_MODE=1
      IMAGE_TAG_CLI="cli-"
      ;;
    --image-path-suffix=*)
      IMAGE_PATH_SUFFIX="${1#*=}"
      ;;
    --help)
        print_help
        exit 0
        ;;
    *)
        if [ -z "$BUILD_IMAGE_TAG" ];
        then
          BUILD_IMAGE_TAG="${1}"
        elif [ -z "$SRCROOTDIR" ];
        then
          SRCROOTDIR="${1}"
        elif [ -z "$REGISTRY" ];
        then
          REGISTRY=${1}
        else
          echo "ERROR: '$1' is not a valid option/positional argument"
          echo
          print_help
          exit 2
        fi
        ;;
    esac
    shift
done

TST_IMGTAG=${BUILD_IMAGE_TAG:?"Missing arg #1 to specify built image tag"}
TST_SRCDIR=${SRCROOTDIR:?"Missing arg #2 to specify source directory"}
TST_REGISTRY=${REGISTRY:?"Missing arg #3 to specify target container registry"}

TST_BEEKEEPER_IMAGE=${BEEKEEPER_IMAGE:?"Missing --beekeeper-source-image to specify beekeeper binary source"}
TST_BASE_IMAGE=${BASE_IMAGE:?"Missing --base-image option to specify base image"}

# Supplement a registry path by trailing slash (if needed)
[[ "${REGISTRY}" != */ ]] && REGISTRY="${REGISTRY}/"

echo "Moving into source root directory: ${SRCROOTDIR}"

pushd "$SRCROOTDIR"

export DOCKER_BUILDKIT=1

CLIVE_IMAGE_TAG_PREFIX="${IMAGE_TAG_PREFIX}${IMAGE_TAG_CLI}instance"
CLIVE_IMAGE_PATH="${REGISTRY}${CLIVE_IMAGE_TAG_PREFIX}${IMAGE_PATH_SUFFIX}"
CLIVE_IMAGE_NAME="${CLIVE_IMAGE_PATH}:${CLIVE_IMAGE_TAG_PREFIX}-${BUILD_IMAGE_TAG}"

docker build --target=${DOCKER_TARGET} \
  --build-arg CI_REGISTRY_IMAGE=$REGISTRY \
  --build-arg BASE_IMAGE=${BASE_IMAGE} \
  --build-arg BEEKEEPER_IMAGE=${BEEKEEPER_IMAGE} \
  --build-arg INTERACTIVE_CLI_MODE=${INTERACTIVE_CLI_MODE} \
  -t ${CLIVE_IMAGE_NAME} \
  -f docker/Dockerfile .

popd

echo "CLIVE_IMAGE_TAG_PREFIX=${CLIVE_IMAGE_TAG_PREFIX}" > docker_image_name.env
echo "CLIVE_IMAGE_PATH=${CLIVE_IMAGE_PATH}" >> docker_image_name.env
echo "CLIVE_IMAGE_NAME=${CLIVE_IMAGE_NAME}" >> docker_image_name.env
