#! /bin/bash

set -euo pipefail

TESTNET_NODE_LOG_FILE=testnet_node.log

wait_for_testnet() {
  LIMIT=120 # seconds
  TARGET_SUBSTRING="Serving forever"
  COMMAND="( tail -f -n0 ${TESTNET_NODE_LOG_FILE} & ) | grep -q '${TARGET_SUBSTRING}'"

  echo "Waiting for testnet node to be ready..."
  timeout $LIMIT bash -c "${COMMAND}"
  echo "Testnet node is ready to use"
}

echo "TESTNET_MODE=${TESTNET_MODE}"
echo "INTERACTIVE_CLI_MODE=${INTERACTIVE_CLI_MODE}"

# Activate the virtual environment
source $(poetry env info --path)/bin/activate

if [ "${TESTNET_MODE}" = "0" ]; then
  if [ "${INTERACTIVE_CLI_MODE}" = "0" ]; then
    echo "Launching clive in TUI mode on mainnet"
    clive
  else
    echo "Launching clive in CLI mode on mainnet"
    clive beekeeper spawn  # Spawn the beekeeper so commands that require it don't have to do it every time
    bash
  fi
else
  if [ "${INTERACTIVE_CLI_MODE}" = "0" ]; then
    echo "Launching clive in TUI mode on testnet"
    python3 testnet_node.py
  else
    echo "Launching clive in CLI mode on testnet"

    python3 testnet_node.py --no-tui >${TESTNET_NODE_LOG_FILE} 2>&1 &
    wait_for_testnet
    clive beekeeper spawn  # Spawn the beekeeper so commands that require it don't have to do it every time
    bash
  fi
fi
