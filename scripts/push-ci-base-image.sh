#! /bin/bash

REGISTRY="registry.gitlab.syncad.com/hive/clive"
BASE_IMAGE="ubuntu20.04"
VERSION="1"

URL="${REGISTRY}/ci-base-image:${BASE_IMAGE}-${VERSION}"

docker manifest inspect "${URL}" > /dev/null 2>&1
EXIT_STATUS=$?
if [ $EXIT_STATUS == 0 ]; then
  echo "Image '${URL}' already exists, skipping push!"
  exit 1
else
  echo "Pushing image '${URL}'"
  docker push "${URL}"
fi
