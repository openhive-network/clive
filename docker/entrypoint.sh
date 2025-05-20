#!/bin/bash

# Exit immediately on error, unset variables are errors, and fail on any command in a pipeline
set -euo pipefail

SCRIPTPATH="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 && pwd -P)"
SELECTED_PROFILE=""
UNLOCK_TIME_MINS=""
TESTNET_NODE_LOG_FILE="testnet_node.log"
INTERACTIVE_CLI_MODE=0

# Print usage/help
print_help() {
  echo "Usage: $0 [OPTION]..."
  echo
  echo "An entrypoint script for the Clive Docker container."
  echo "OPTIONS:"
  echo "  --cli                 Launch Clive in the interactive CLI mode (default is TUI)"
  echo "  --profile-name NAME   Name of profile that will be used, default is profile selection."
  echo "  --unlock-time MINUTES Unlock time in minutes, default is no timeout for unlock."
  echo "  --exec FILE           Path to bash script to be executed."
  echo "  -h, --help            Display this help screen and exit"
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
        #echo "Setting user clive's UID to '${CLIVE_UID}'"
        usermod -o -u "${CLIVE_UID}" clive
      fi
      #echo "Respawning entrypoint as user clive"
      exec sudo -HEnu clive /bin/bash "${SCRIPTPATH}/entrypoint.sh" "$@"
      exit 0
    fi
  fi
}

# Wait for the testnet node to be ready before proceeding
wait_for_testnet() {
  local limit=120 #seconds
  local target_substring="Serving forever"
  local command="while [ ! -f ${TESTNET_NODE_LOG_FILE} ]; do sleep 1; done; (tail -f -n0 ${TESTNET_NODE_LOG_FILE} &) | grep -q '${target_substring}'"

  echo "Waiting for testnet node to be ready..."
  timeout "$limit" bash -c "${command}"
  echo "Testnet node is ready to use."
}

# Launch Clive in CLI mode
launch_cli() {
  echo 'PS1="\u@cli:\w\$ "' >> ~/.bashrc
  clive --install-completion >/dev/null 2>&1
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
      --profile-name)
        shift
        SELECTED_PROFILE="$1"
        export SELECTED_PROFILE
        ;;
      --unlock-time)
        shift
        UNLOCK_TIME_MINS="$1"
        export UNLOCK_TIME_MINS
        ;;
      -h|--help)
        print_help
        exit 0
        ;;
      -*)
        echo "ERROR: '$1' is not a valid option"
        echo
        print_help
        exit 1
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
    echo "Launching clive in TUI mode on mainnet"
    exec clive
  else
    echo "Launching clive in CLI mode on mainnet"
    launch_cli
  fi
}

# Main execution logic for testnet
run_testnet() {
  if [[ "${INTERACTIVE_CLI_MODE}" = "0" ]]; then
    echo "Launching clive in TUI mode on testnet"
    exec python3 testnet_node.py -p -t
  else
    echo "Launching clive in CLI mode on testnet"
    # We use setsid to detach from the process group because ctrl-c will kill the testnet_node.py
    setsid python3 testnet_node.py -p >${TESTNET_NODE_LOG_FILE} 2>&1 &
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
