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

BEEKEEPER_IMAGE=""
BASE_IMAGE=""


print_help () {
    echo "Usage: $0 <image_tag> <src_dir> <registry_url> [OPTION[=VALUE]]..."
    echo
    echo "Allows to build docker image containing clive installation"
    echo "OPTIONS:"
    echo "  --beekeeper-source-image=image_name Allows to specify image name containing a prebuilt beekeper tool"
    echo "  --base-image=image_name             Allows to specify an image name being use as a base of the one to be built"
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
#pwd

export DOCKER_BUILDKIT=1

docker build --target=instance \
  --build-arg CI_REGISTRY_IMAGE=$REGISTRY \
  --build-arg BASE_IMAGE=${BASE_IMAGE} \
  --build-arg BEEKEEPER_IMAGE=${BEEKEEPER_IMAGE} \
  -t ${REGISTRY}${IMAGE_TAG_PREFIX}instance:${IMAGE_TAG_PREFIX}instance-${BUILD_IMAGE_TAG} \
  -f docker/Dockerfile .

popd

echo "CLIVE_IMAGE_NAME=${REGISTRY}${IMAGE_TAG_PREFIX}instance:${IMAGE_TAG_PREFIX}instance-${BUILD_IMAGE_TAG}" > docker_image_name.env
