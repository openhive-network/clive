#!/bin/bash

# Exit immediately on error, unset variables are errors, and fail on any command in a pipeline
set -euo pipefail

SCRIPTPATH="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 && pwd -P)"
TESTNET_NODE_LOG_FILE="testnet_node.log"
INTERACTIVE_CLI_MODE=0
CLIVE_ARGS=()

# Add Clive argument to the Clive args array
add_clive_arg() {
    CLIVE_ARGS+=("$1")
}

# Print usage/help
print_help() {
  echo "Usage: $0 [OPTION]..."
  echo
  echo "An entrypoint script for the Clive Docker container."
  echo "OPTIONS:"
  echo "  --cli                Launch Clive in the interactive CLI mode (default is TUI)"
  echo "  --exec FILE          Path to bash script to be executed."
  echo "  -h, --help           Display this help screen and exit"
  echo "  -*                   Pass argument that will be used with init Clive command"
  echo
}

# Check if running as root, and if necessary, switch user and re-execute script
check_and_switch_user() {
  if [[ "$EUID" -eq 0 ]]; then
    if [[ -z "${CLIVE_UID:-}" ]]; then
      echo "Warning: CLIVE_UID is not set or empty." >&2
    elif ! [[ "${CLIVE_UID}" =~ ^[0-9]+$ ]]; then
      echo "Error: CLIVE_UID is set to '${CLIVE_UID}' and not an integer. Exiting..." >&2
      exit 1
    elif [[ "${CLIVE_UID}" -ne 0 ]]; then
      if [[ "${CLIVE_UID}" -ne "$(id -u clive)" ]]; then
        echo "Setting user clive's UID to '${CLIVE_UID}'"
        usermod -o -u "${CLIVE_UID}" clive
      fi
      echo "Respawning entrypoint as user clive"
      exec sudo -HEnu clive /bin/bash "${SCRIPTPATH}/entrypoint.sh" "$@"
      exit 0
    fi
  fi
}

# Wait for the testnet node to be ready before proceeding
wait_for_testnet() {
  local limit=120 #seconds
  local target_substring="Serving forever"
  local command="(tail -f -n0 ${TESTNET_NODE_LOG_FILE} &) | grep -q '${target_substring}'"

  echo "Waiting for testnet node to be ready..."
  timeout "$limit" bash -c "${command}"
  echo "Testnet node is ready to use."
}
# Launch Clive in CLI mode
launch_cli() {
  clive --install-completion >/dev/null 2>&1
  if [ ${#CLIVE_ARGS[@]} -ne 0 ]; then
    clive "${CLIVE_ARGS[@]}"
  fi
  exec bash --init-file /clive/scripts/activate_beekeeper.sh
}

# Parse command-line arguments
parse_arguments() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --cli)
        INTERACTIVE_CLI_MODE=1
        ;;
      --exec)
        shift
        FILE_TO_EXECUTE="$1"
        export FILE_TO_EXECUTE
        ;;
      -h|--help)
        print_help
        exit 0
        ;;
      -*)
        local arg="${1#-}"
        add_clive_arg "$arg"
        ;;
      *)
        echo "ERROR: '$1' is not a valid argument"
        echo
        print_help
        exit 2
        ;;
    esac
    shift
  done
}

# Activate Python virtual environment
activate_virtualenv() {
  cd /clive || exit 1
  # shellcheck source=/dev/null
  source "${PYTHON_VENV_PATH}/bin/activate"
}

# Main execution logic for mainnet
run_mainnet() {
  if [[ "${INTERACTIVE_CLI_MODE}" = "0" ]]; then
    echo "Launching Clive in TUI mode on mainnet"
    exec clive
  else
    echo "Launching Clive in CLI mode on mainnet"
    launch_cli
  fi
}

# Main execution logic for testnet
run_testnet() {
  if [[ "${INTERACTIVE_CLI_MODE}" = "0" ]]; then
    echo "Launching Clive in TUI mode on testnet"
    exec python3 testnet_node.py
  else
    echo "Launching Clive in CLI mode on testnet"
    python3 testnet_node.py --no-tui >"${TESTNET_NODE_LOG_FILE}" 2>&1 &
    wait_for_testnet
    launch_cli
  fi
}

# Main function to drive the script
main() {
  check_and_switch_user "$@"
  parse_arguments "$@"
  activate_virtualenv

  if [[ "${TESTNET_MODE}" = "0" ]]; then
    run_mainnet
  else
    run_testnet
  fi
}

# Entry point of the script
main "$@"
