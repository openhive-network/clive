#!/usr/bin/env bash
# Build (and with --push, publish) the test runtime image of .aidev/runtime/Dockerfile
# and print the digest-pinned reference to put in .aidev/project.yaml's
# `environment.image`. See .aidev/README.md.
#
# The tag is `aidev-<hash>` of the image inputs (the Dockerfile, pyproject.toml,
# poetry.lock, tests/clive-local-tools/{pyproject.toml,poetry.lock}). When
# <repository>:aidev-<hash> is already in the registry nothing is built: the script
# prints its digest.
#
#   .aidev/runtime/build.sh           # registry digest, or build locally and print the local tag
#   .aidev/runtime/build.sh --push    # registry digest, or build + push and print repo@sha256:<digest>
#   .aidev/runtime/build.sh --tag     # print the input-hash tag only
#
# AIDEV_RUNTIME_BUILDER picks the buildx builder (e.g. one whose buildkitd mirrors
# registry.gitlab.syncad.com); the default is the current builder.
set -euo pipefail
cd "$(dirname "$0")/../.."
REPOSITORY="${AIDEV_RUNTIME_REPOSITORY:-registry.gitlab.syncad.com/hive/clive/aidev-tests}"
LT=tests/clive-local-tools
input_hash() {
    sha256sum .aidev/runtime/Dockerfile pyproject.toml poetry.lock "$LT/pyproject.toml" "$LT/poetry.lock" \
        | sha256sum | cut -c1-16
}
TAG="aidev-$(input_hash)"
case "${1:-}" in
    --tag) echo "$TAG"; exit 0 ;;
    ""|--push) ;;
    *) echo "usage: $0 [--push|--tag]" >&2; exit 2 ;;
esac
registry_digest() {
    docker buildx imagetools inspect "$REPOSITORY:$TAG" --format '{{json .Manifest}}' 2>/dev/null \
        | grep -o '"digest": *"sha256:[0-9a-f]*"' | head -1 | grep -o 'sha256:[0-9a-f]*' || true
}
digest="$(registry_digest)"
if [ -n "$digest" ]; then
    echo "$REPOSITORY:$TAG exists in the registry; not building" >&2
    echo "$REPOSITORY@$digest"
    exit 0
fi
echo "$REPOSITORY:$TAG is not in the registry; building it" >&2
context="$(mktemp -d)"
trap 'rm -rf "$context"' EXIT
mkdir -p "$context/py/tests"
cp pyproject.toml poetry.lock "$context/py/"
cp -r "$LT" "$context/py/tests/"
rm -rf "$context/py/$LT/"*.egg-info
find "$context/py/$LT" -name __pycache__ -prune -exec rm -rf {} +

# buildx so it works with any builder (a docker-container builder keeps no local
# image); no provenance, so the pushed digest is a plain image manifest.
build=(docker buildx build ${AIDEV_RUNTIME_BUILDER:+--builder "$AIDEV_RUNTIME_BUILDER"} --pull --provenance=false
       -f .aidev/runtime/Dockerfile -t "$REPOSITORY:$TAG")
if [ "${1:-}" != "--push" ]; then
    "${build[@]}" --load "$context" >&2
    echo "$REPOSITORY:$TAG"
    exit 0
fi
"${build[@]}" --push --metadata-file "$context/metadata.json" "$context" >&2
digest="$(grep -o '"containerimage.digest": *"sha256:[0-9a-f]*"' "$context/metadata.json" | grep -o 'sha256:[0-9a-f]*')"
echo "$REPOSITORY@${digest:?no digest in buildx metadata}"
