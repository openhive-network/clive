#! /bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit 1; pwd -P )"
echo "$SCRIPTPATH"

export LOG_FILE=run_instance.log
# shellcheck source=scripts/common.sh
source "$SCRIPTPATH/common.sh"

log_exec_params "$@"

# Script responsible for starting a docker container built for image specified at command line.

print_help () {
    echo "Usage: $0 <docker_img> [OPTION[=VALUE]]... [<hived_option>]..."
    echo
    echo "Allows to start docker container for a pointed clive docker image."
    echo "OPTIONS:"
    echo "  --name=CONTAINER_NAME                 Allows to specify a dedicated name to the spawned container instance"
    echo "  --detach                              Allows to start container instance in detached mode. Otherwise, you can detach using Ctrl+p+q key binding"
    echo "  --docker-option=OPTION                Allows to specify additional docker option, to be passed to underlying docker run spawn."
    echo "  --help                                Display this help screen and exit"
    echo
}

DOCKER_ARGS=()
CLIVE_ARGS=()

CONTAINER_NAME=clive-instance
IMAGE_NAME=

add_docker_arg() {
  local arg="$1"
#  echo "Processing docker argument: ${arg}"

  DOCKER_ARGS+=("$arg")
}

add_clive_arg() {
  local arg="$1"
#  echo "Processing hived argument: ${arg}"

  CLIVE_ARGS+=("$arg")
}

while [ $# -gt 0 ]; do
  case "$1" in
     --name=*)
        CONTAINER_NAME="${1#*=}"
        echo "Container name is: $CONTAINER_NAME"
        ;;
    --detach)
      add_docker_arg "--detach"
      ;;

    --docker-option=*)
        options_string="${1#*=}"
        IFS=" " read -ra options <<< "$options_string"
        for option in "${options[@]}"; do
          add_docker_arg "$option"
        done
        ;;
    --help)
        print_help
        exit 0
        ;;
     -*)
        add_clive_arg "$1"
        ;;
     *)
        IMAGE_NAME="${1}"
        echo "Using image name: $IMAGE_NAME"
        ;;
    esac
    shift
done

# Collect remaining command line args to pass to the container to run
CMD_ARGS=("$@")

if [ -z "$IMAGE_NAME" ]; then
  echo "Error: Missing docker image name."
  echo "Usage: $0 <docker_img> [OPTION[=VALUE]]... [<hived_option>]..."
  echo
  exit 1
fi

CMD_ARGS+=("${CLIVE_ARGS[@]}")

#echo "Using docker image: $IMAGE_NAME"
#echo "Additional hived args: ${CMD_ARGS[@]}"

# If command 'tput' exists
if command -v tput &> /dev/null
then
  add_docker_arg "--env"
  add_docker_arg "COLUMNS=$(tput cols)"
  add_docker_arg "--env"
  add_docker_arg "LINES=$(tput lines)"
fi

docker container rm -f -v "$CONTAINER_NAME" 2>/dev/null || true
docker run --rm -it -e HIVED_UID="$(id -u)" --name "$CONTAINER_NAME" --stop-timeout=180 "${DOCKER_ARGS[@]}" "${IMAGE_NAME}" "${CMD_ARGS[@]}"
