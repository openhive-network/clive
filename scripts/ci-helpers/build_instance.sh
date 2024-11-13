#! /bin/bash
set -euo pipefail

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
SCRIPTSDIR="$SCRIPTPATH/.."

export LOG_FILE=build_instance.log
# shellcheck source=scripts/common.sh
source "$SCRIPTSDIR/common.sh"

BUILD_IMAGE_TAG=""
REGISTRY=""
SRCROOTDIR=""

IMAGE_TAG_PREFIX=""

HIVED_IMAGE=""
BASE_IMAGE=""

CLIVE_VERSION=""

DOCKER_TARGET="instance"

print_help () {
    echo "Usage: $0 <image_tag> <src_dir> <registry_url> [OPTION[=VALUE]]..."
    echo
    echo "Allows to build docker image containing clive installation"
    echo "For example:, produced mainnet image will be named: registry.gitlab.syncad.com/hive/clive:<image_tag>"
    echo "  - produced mainnet image will be named: registry.gitlab.syncad.com/hive/clive:<image_tag>"
    echo "  - produced testnet image will be named: registry.gitlab.syncad.com/hive/clive:testnet-<image_tag>"
    echo "OPTIONS:"
    echo "  --hived-source-image=image_name     Allows to specify image name containing a prebuilt hived"
    echo "  --base-image=image_name             Allows to specify an image name being use as a base of the one to be built"
    echo "  --clive-version=version             Allows to specify a version of clive to be installed in the image"
    echo "  --embedded-testnet                  Allows to build a clive image having embedded a hived testnet inside (ready for immediate sanboxing run)"
    echo "  --help                              Display this help screen and exit"
    echo
}

while [ $# -gt 0 ]; do
  case "$1" in
    --hived-source-image=*)
      HIVED_IMAGE="${1#*=}"
      echo "Specified Hived source image: ${HIVED_IMAGE}"
      ;;
    --base-image=*)
      BASE_IMAGE="${1#*=}"
      echo "Specified base image: ${BASE_IMAGE}"
      ;;
    --clive-version=*)
      CLIVE_VERSION="${1#*=}"
      echo "Specified clive version: ${CLIVE_VERSION}"
      ;;
    --embedded-testnet)
      DOCKER_TARGET="embedded_testnet_instance"
      IMAGE_TAG_PREFIX="testnet-"
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

_TST_IMGTAG=${BUILD_IMAGE_TAG:?"Missing arg #1 to specify built image tag"}
_TST_SRCDIR=${SRCROOTDIR:?"Missing arg #2 to specify source directory"}
_TST_REGISTRY=${REGISTRY:?"Missing arg #3 to specify target container registry"}

_TST_HIVED_IMAGE=${HIVED_IMAGE:?"Missing --hived-source-image to specify source for binaries of hived"}
_TST_BASE_IMAGE=${BASE_IMAGE:?"Missing --base-image option to specify base image"}
_TST_CLIVE_VERSION=${CLIVE_VERSION:?"Missing --clive-version option to specify clive version to be installed"}

# STRIP a registry path from optional trailing slash (if needed) to use it as an image base pathname
CLIVE_IMAGE_PATH="${REGISTRY}"
[[ "${REGISTRY}" == */ ]] && CLIVE_IMAGE_PATH="${REGISTRY%/}"

# Supplement a registry path by trailing slash (if needed)
[[ "${REGISTRY}" != */ ]] && REGISTRY="${REGISTRY}/"

echo "Using an image pathname: ${CLIVE_IMAGE_PATH}"
echo "Moving into source root directory: ${SRCROOTDIR}"

pushd "$SRCROOTDIR"

CLIVE_IMAGE_NAME="${CLIVE_IMAGE_PATH}:${IMAGE_TAG_PREFIX}${BUILD_IMAGE_TAG}"

BUILD_TIME="$(date -uIseconds)"

GIT_COMMIT_SHA="$(git rev-parse HEAD || true)"
if [ -z "$GIT_COMMIT_SHA" ]; then
  GIT_COMMIT_SHA="[unknown]"
fi

GIT_CURRENT_BRANCH="$(git branch --show-current || true)"
if [ -z "$GIT_CURRENT_BRANCH" ]; then
  GIT_CURRENT_BRANCH="$(git describe --abbrev=0 --all | sed 's/^.*\///' || true)"
  if [ -z "$GIT_CURRENT_BRANCH" ]; then
    GIT_CURRENT_BRANCH="[unknown]"
  fi
fi

GIT_LAST_LOG_MESSAGE="$(git log -1 --pretty=%B || true)"
if [ -z "$GIT_LAST_LOG_MESSAGE" ]; then
  GIT_LAST_LOG_MESSAGE="[unknown]"
fi

GIT_LAST_COMMITTER="$(git log -1 --pretty="%an <%ae>" || true)"
if [ -z "$GIT_LAST_COMMITTER" ]; then
  GIT_LAST_COMMITTER="[unknown]"
fi

GIT_LAST_COMMIT_DATE="$(git log -1 --pretty="%aI" || true)"
if [ -z "$GIT_LAST_COMMIT_DATE" ]; then
  GIT_LAST_COMMIT_DATE="[unknown]"
fi

docker buildx build --target="${DOCKER_TARGET}" \
  --build-arg CI_REGISTRY_IMAGE="$REGISTRY" \
  --build-arg BASE_IMAGE="${BASE_IMAGE}" \
  --build-arg HIVED_IMAGE="${HIVED_IMAGE}" \
  --build-arg CLIVE_VERSION="${CLIVE_VERSION}" \
  --build-arg BUILD_TIME="${BUILD_TIME}" \
  --build-arg GIT_COMMIT_SHA="${GIT_COMMIT_SHA}" \
  --build-arg GIT_CURRENT_BRANCH="${GIT_CURRENT_BRANCH}" \
  --build-arg GIT_LAST_LOG_MESSAGE="${GIT_LAST_LOG_MESSAGE}" \
  --build-arg GIT_LAST_COMMITTER="${GIT_LAST_COMMITTER}" \
  --build-arg GIT_LAST_COMMIT_DATE="${GIT_LAST_COMMIT_DATE}" \
  --tag "${CLIVE_IMAGE_NAME}" \
  --tag "${REGISTRY}minimal-instance:${IMAGE_TAG_PREFIX}${BUILD_IMAGE_TAG}" \
  --tag "${REGISTRY}instance:${IMAGE_TAG_PREFIX}${BUILD_IMAGE_TAG}" \
  --load \
  --file docker/Dockerfile .

popd

echo "CLIVE_IMAGE_PATH=${CLIVE_IMAGE_PATH}" >> docker_image_name.env
echo "CLIVE_IMAGE_NAME=${CLIVE_IMAGE_NAME}" >> docker_image_name.env
