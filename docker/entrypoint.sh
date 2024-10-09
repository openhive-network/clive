#!/bin/bash

set -euo pipefail

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"


if [[ "$EUID" -eq 0 ]]; then
  if [[ -z "${CLIVE_UID:-}" ]]; then
    echo "Warning: variable CLIVE_UID is not set or set to an empty value." >&2
  elif ! [[ "${CLIVE_UID}" =~ ^[0-9]+$ ]] ; then
    echo "Error: variable CLIVE_UID is set to '${CLIVE_UID}' and not an integer. Exiting..." >&2
    exit 1
  elif [[ "${CLIVE_UID}" -ne 0 ]];
  then
    if [[ "${CLIVE_UID}" -ne $(id -u clive) ]];
    then
      echo "Setting user clive's UID to value '${CLIVE_UID}'"
      usermod -o -u "${CLIVE_UID}" clive
    fi

    echo "Respawning entrypoint as user clive"
    exec sudo -HEnu clive /bin/bash "${SCRIPTPATH}/entrypoint.sh" "$@"
    exit 0
  fi
fi

TESTNET_NODE_LOG_FILE=testnet_node.log

print_help() {
  echo "Usage: $0 [OPTION]..."
  echo
  echo "An entrypoint script for the clive docker container."
  echo "OPTIONS:"
  echo "  --cli                                 Launch clive in the interactive CLI mode (default is TUI)"
  echo "  --exec PATH_TO_FILE                   Path to bash script to be executed."
  echo "  -h / --help                           Display this help screen and exit"
  echo
}

wait_for_testnet() {
  LIMIT=120 # seconds
  TARGET_SUBSTRING="Serving forever"
  COMMAND="( tail -f -n0 ${TESTNET_NODE_LOG_FILE} & ) | grep -q '${TARGET_SUBSTRING}'"

  echo "Waiting for testnet node to be ready..."
  timeout $LIMIT bash -c "${COMMAND}"
  echo "Testnet node is ready to use"
}

execute_passed_script(){
  if [ -n "${FILE_TO_EXECUTE:-}" ]; then
      if [ -f "${FILE_TO_EXECUTE}" ]; then
          echo "Executing file: ${FILE_TO_EXECUTE}"
          # shellcheck disable=SC1090
          source "./${FILE_TO_EXECUTE}"
      else
          echo "Error: ${FILE_TO_EXECUTE} does not exist or is not a file."
          exit 1
      fi
  fi
}

launch_cli() {
  execute_passed_script
  clive --install-completion >/dev/null 2>&1
  clive beekeeper spawn # Spawn the beekeeper so commands that require it don't have to do it every time
  bash
  clive beekeeper close
}

INTERACTIVE_CLI_MODE=0

while [ $# -gt 0 ]; do
  case "$1" in
  --cli)
    INTERACTIVE_CLI_MODE=1
    ;;
  --exec)
    shift
    FILE_TO_EXECUTE="$1"
    ;;
  -h | --help)
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

cd /clive
# shellcheck source=/dev/null
source "${PYTHON_VENV_PATH}/bin/activate"

if [ "${TESTNET_MODE}" = "0" ]; then
  if [ "${INTERACTIVE_CLI_MODE}" = "0" ]; then
    echo "Launching clive in TUI mode on mainnet"
    exec clive
  else
    echo "Launching clive in CLI mode on mainnet"
    launch_cli
  fi
else
  if [ "${INTERACTIVE_CLI_MODE}" = "0" ]; then
    echo "Launching clive in TUI mode on testnet"
    exec python3 testnet_node.py
  else
    echo "Launching clive in CLI mode on testnet"

    python3 testnet_node.py --no-tui >${TESTNET_NODE_LOG_FILE} 2>&1 &
    wait_for_testnet
    launch_cli
  fi
fi
