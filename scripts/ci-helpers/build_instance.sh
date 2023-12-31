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
IMAGE_PATH_SUFFIX=""

HIVED_IMAGE=""
BASE_IMAGE=""

CLIVE_VERSION=""

DOCKER_TARGET="instance"

print_help () {
    echo "Usage: $0 <image_tag> <src_dir> <registry_url> [OPTION[=VALUE]]..."
    echo
    echo "Allows to build docker image containing clive installation"
    echo "OPTIONS:"
    echo "  --hived-source-image=image_name     Allows to specify image name containing a prebuilt hived"
    echo "  --base-image=image_name             Allows to specify an image name being use as a base of the one to be built"
    echo "  --clive-version=version             Allows to specify a version of clive to be installed in the image"
    echo "  --embedded-testnet                  Allows to build a clive image having embedded a hived testnet inside (ready for immediate sanboxing run)"
    echo "  --image-path-suffix                 Allows to specify a suffix to be added to the image path, to organize images in a more structured directory-like way"
    echo "  --help                              Display this help screen and exit"
    echo
}

EXPORT_PATH=""

while [ $# -gt 0 ]; do
  case "$1" in
    --hived-source-image=*)
      HIVED_IMAGE="${1#*=}"
      ;;
    --base-image=*)
      BASE_IMAGE="${1#*=}"
      ;;
    --clive-version=*)
      CLIVE_VERSION="${1#*=}"
      ;;
    --embedded-testnet)
      DOCKER_TARGET="embedded_testnet_instance"
      IMAGE_TAG_PREFIX="testnet-"
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

TST_HIVED_IMAGE=${HIVED_IMAGE:?"Missing --hived-source-image to specify source for binaries of hived"}
TST_BASE_IMAGE=${BASE_IMAGE:?"Missing --base-image option to specify base image"}
TST_CLIVE_VERSION=${CLIVE_VERSION:?"Missing --clive-version option to specify clive version to be installed"}

# Supplement a registry path by trailing slash (if needed)
[[ "${REGISTRY}" != */ ]] && REGISTRY="${REGISTRY}/"

echo "Moving into source root directory: ${SRCROOTDIR}"

pushd "$SRCROOTDIR"

export DOCKER_BUILDKIT=1

CLIVE_IMAGE_TAG_PREFIX="${IMAGE_TAG_PREFIX}instance"
CLIVE_IMAGE_PATH="${REGISTRY}${CLIVE_IMAGE_TAG_PREFIX}${IMAGE_PATH_SUFFIX}"
CLIVE_IMAGE_NAME="${CLIVE_IMAGE_PATH}:${CLIVE_IMAGE_TAG_PREFIX}-${BUILD_IMAGE_TAG}"

docker build --target=${DOCKER_TARGET} \
  --build-arg CI_REGISTRY_IMAGE=$REGISTRY \
  --build-arg BASE_IMAGE=${BASE_IMAGE} \
  --build-arg HIVED_IMAGE=${HIVED_IMAGE} \
  --build-arg CLIVE_VERSION=${CLIVE_VERSION} \
  -t ${CLIVE_IMAGE_NAME} \
  -f docker/Dockerfile .

popd

echo "CLIVE_IMAGE_TAG_PREFIX=${CLIVE_IMAGE_TAG_PREFIX}" > docker_image_name.env
echo "CLIVE_IMAGE_PATH=${CLIVE_IMAGE_PATH}" >> docker_image_name.env
echo "CLIVE_IMAGE_NAME=${CLIVE_IMAGE_NAME}" >> docker_image_name.env
