#! /bin/bash

set -euo pipefail

TESTNET_NODE_LOG_FILE=testnet_node.log

print_help() {
  echo "Usage: $0 [OPTION]..."
  echo
  echo "An entrypoint script for the clive docker container."
  echo "OPTIONS:"
  echo "  --cli                                 Launch clive in the interactive CLI mode (default is TUI)"
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

launch_cli() {
  clive --install-completion >/dev/null 2>&1
  clive beekeeper spawn # Spawn the beekeeper so commands that require it don't have to do it every time
  bash
}

INTERACTIVE_CLI_MODE=0

while [ $# -gt 0 ]; do
  case "$1" in
  --cli)
    INTERACTIVE_CLI_MODE=1
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

echo "/home/clive_admin"
ls -al /home/clive_admin

echo "/home/clive_admin/.clive"
ls -al /home/clive_admin/.clive

if [ "${TESTNET_MODE}" = "0" ]; then
  if [ "${INTERACTIVE_CLI_MODE}" = "0" ]; then
    echo "Launching clive in TUI mode on mainnet"
    clive
  else
    echo "Launching clive in CLI mode on mainnet"
    launch_cli
  fi
else
  if [ "${INTERACTIVE_CLI_MODE}" = "0" ]; then
    echo "Launching clive in TUI mode on testnet"
    python3 testnet_node.py
  else
    echo "Launching clive in CLI mode on testnet"

    python3 testnet_node.py --no-tui >${TESTNET_NODE_LOG_FILE} 2>&1 &
    wait_for_testnet
    launch_cli
  fi
fi
