#!/bin/bash

# Exit immediately on error, unset variables are errors, and fail on any command in a pipeline
set -euo pipefail

# Source the common base script
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit 1; pwd -P )"
BASE_SCRIPT="${SCRIPTPATH}"/base.sh
if [ ! -f "${BASE_SCRIPT}" ]; then
  echo "Error: ${BASE_SCRIPT} does not exist or is not a file."
  echo "Error: Please generate one using ./ci-helpers/generate_startup_scripts.sh"
  exit 1
fi
# shellcheck disable=SC1090
source "$BASE_SCRIPT"

# Set the container name for CLI mode
CONTAINER_NAME="clive-cli-$(date +%s)"
export CONTAINER_NAME

# Print usage information for the script
print_help() {
    echo "Usage: $0 [<docker_img>] [OPTION[=VALUE]]... [<clive_option>]..."
    echo
    echo "Allows to start Clive application in CLI mode."
    echo "OPTIONS:"
    echo "  --data-dir=DIRECTORY_PATH      Points to a Clive data directory to store profile data. Defaults to ${HOME}/.clive directory."
    echo "  --docker-option=OPTION         Allows specifying additional Docker options to pass to underlying Docker run."
    echo "  --exec=PATH_TO_FILE            Path to bash script to be executed."
    echo "  --help                         Display this help screen and exit."
    echo
}

# Get the WORKINGDIR from containers image
get_workdir() {
    docker inspect --format='{{.Config.WorkingDir}}' "$IMAGE_NAME"
}

# Override parse_args to handle --exec flag specifically for CLI mode
parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --exec)
                shift
                FILE_TO_MOUNT="${1}"
                WORKDIR=$(get_workdir)
                if [ -z "$WORKDIR" ]; then
                    echo "Error: Could not retrieve WORKDIR for image: $IMAGE_NAME"
                    exit 1
                fi

                FILE_TO_MOUNT_NAME=$(basename "$FILE_TO_MOUNT")

                MOUNT_TARGET="${WORKDIR}/${FILE_TO_MOUNT_NAME}"
                add_docker_arg "--volume"
                add_docker_arg "${FILE_TO_MOUNT}:${MOUNT_TARGET}"
                add_clive_arg "--exec"
                add_clive_arg "${FILE_TO_MOUNT_NAME}"
                ;;
            --exec=*)
                FILE_TO_MOUNT="${1#*=}"
                WORKDIR=$(get_workdir)
                if [ -z "$WORKDIR" ]; then
                    echo "Error: Could not retrieve WORKDIR for image: $IMAGE_NAME"
                    exit 1
                fi

                FILE_TO_MOUNT_NAME=$(basename "$FILE_TO_MOUNT")

                MOUNT_TARGET="${WORKDIR}/${FILE_TO_MOUNT_NAME}"
                add_docker_arg "--volume"
                add_docker_arg "${FILE_TO_MOUNT}:${MOUNT_TARGET}"
                add_clive_arg "--exec"
                add_clive_arg "${FILE_TO_MOUNT_NAME}"
                ;;
            *)
            new_args+=("$1")
            ;;
        esac
        shift
    done
    common_parse_args "${new_args[@]}"
}

# Add the --cli flag to Clive arguments
add_clive_arg "--cli"

# Run the main function, passing the extended parse_args
main "$@"
