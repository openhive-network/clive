#!/bin/bash

# Exit immediately on error, unset variables are errors, and fail on any command in a pipeline
set -euo pipefail

# Source the common base script
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 || exit 1; pwd -P )"
BASE_SCRIPT="${SCRIPTPATH}"/base.sh
if ! [ -f "${BASE_SCRIPT}" ]; then
  echo "Error: ${BASE_SCRIPT} does not exist or is not a file."
  echo "Error: Please generate one using ./ci-helpers/generate_startup_scripts.sh"
  exit 1
fi
# shellcheck disable=SC1090
source "$BASE_SCRIPT"


# Set the container name for TUI mode
CONTAINER_NAME="clive-tui-$(date +%s)"
export CONTAINER_NAME

# Print usage information for the script
print_help() {
    echo "Usage: $0 [<docker_img>] [OPTION[=VALUE]]... [<clive_option>]..."
    echo
    echo "Allows to start Clive application in TUI mode."
    echo "OPTIONS:"
    echo "  --data-dir=DIRECTORY_PATH      Points to a Clive data directory to store profile data. Defaults to ${HOME}/.clive directory."
    echo "  --docker-option=OPTION         Allows specifying additional Docker options to pass to underlying Docker run."
    echo "  --help                         Display this help screen and exit."
    echo
}

# Run the main function defined in the base script
main "$@"
