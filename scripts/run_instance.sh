#! /bin/bash

# Script responsible for starting a docker container built for image specified at command line.

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit 1; pwd -P )"
#echo "$SCRIPTPATH"

CURRENT_WORKING_DIR="$(pwd)"
#echo "$CURRENT_WORKING_DIR"

export LOG_FILE="run_instance.log"
# shellcheck source=scripts/common.sh
source "${SCRIPTPATH}/common.sh"

#log_exec_params "$@"

print_help () {
    echo "${USAGE_MSG}"
    echo
    echo "Allows to start docker container for a pointed clive docker image."
    echo "It's recommended to use official clive docker images available at https://hub.docker.com/r/hiveio/clive/tags"
    echo
    echo "OPTIONS:"
    echo "  --name=<CONTAINER_NAME> (=${CONTAINER_NAME})    Allows to specify a dedicated name to the spawned container instance."
    echo "  --data-dir=<PATH> (=<CWD>/${HOST_DATA_DIR_NAME})        Allows to specify path where clive data will be stored (mapped) on the host."
    echo "  --cli                                        Allows to launch clive in the CLI mode (by default, without this, TUI will be launched)."
    echo "  --detach                                     Allows to start container instance in detached mode. Otherwise, you can detach using Ctrl+@, Ctrl+Q key binding sequence."
    echo "  --docker-option=<OPTION>                     Allows to specify additional docker option, to be passed to underlying docker run spawn."
    echo "  --help                                       Display this help screen and exit."
    echo
}

USAGE_MSG="Usage: ${0} <docker_img> [OPTION[=VALUE]]..."

DOCKER_ARGS=()
ENTRYPOINT_ARGS=()

CONTAINER_NAME="clive-instance"
IMAGE_NAME=""

HOST_DATA_DIR_NAME="clive-data"
HOST_DATA_DIR="${CURRENT_WORKING_DIR}/${HOST_DATA_DIR_NAME}"
INTERNAL_DATA_DIR="/root/.clive"

add_docker_arg() {
  local arg="${1}"
#  echo "Processing docker argument: ${arg}"

  DOCKER_ARGS+=("${arg}")
}

add_entrypoint_arg() {
  local arg="${1}"
#  echo "Processing entrypoint argument: ${arg}"

  ENTRYPOINT_ARGS+=("${arg}")
}

while [ $# -gt 0 ]; do
  case "${1}" in
     --name=*)
        CONTAINER_NAME="${1#*=}"
        echo "Container name is: ${CONTAINER_NAME}"
        ;;
    --cli)
      add_entrypoint_arg "--cli"
      ;;
    --data-dir=*)
      HOST_DATA_DIR="${1#*=}"
      ;;
    --detach)
      add_docker_arg "--detach"
      ;;

    --docker-option=*)
        options_string="${1#*=}"
        IFS=" " read -ra options <<< "${options_string}"
        for option in "${options[@]}"; do
          add_docker_arg "${option}"
        done
        ;;
    --help)
        print_help
        exit 0
        ;;
     -*)
        echo "Error: Unrecognized option: ${1}"
        echo "${USAGE_MSG}"
        exit 1
        ;;
     *)
        IMAGE_NAME="${1}"
        echo "Using image name: ${IMAGE_NAME}"
        ;;
    esac
    shift
done


if [ -z "${IMAGE_NAME}" ]; then
  echo "Error: Missing docker image name."
  echo "${USAGE_MSG}"
  echo
  exit 1
fi

# If command 'tput' exists
if command -v tput &> /dev/null
then
  add_docker_arg "--env"
  add_docker_arg "COLUMNS=$(tput cols)"
  add_docker_arg "--env"
  add_docker_arg "LINES=$(tput lines)"
fi

add_docker_arg "--detach-keys=ctrl-@,ctrl-q"

add_docker_arg "--volume"
add_docker_arg "${HOST_DATA_DIR}:${INTERNAL_DATA_DIR}"

#echo "Using docker image: ${IMAGE_NAME}"
#echo "Additional docker args: ${DOCKER_ARGS[@]}"
#echo "Additional entrypoint args: ${ENTRYPOINT_ARGS[@]}"

docker container rm -f -v "${CONTAINER_NAME}" 2>/dev/null || true
docker run --rm -it -e HIVED_UID="$(id -u)" --name "${CONTAINER_NAME}" --stop-timeout=180 "${DOCKER_ARGS[@]}" "${IMAGE_NAME}" "${ENTRYPOINT_ARGS[@]}"
