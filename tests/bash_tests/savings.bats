#!/usr/bin/env bats

setup() {
  if test -d "$(pwd)/generated_clive_data/$BATS_TEST_NAME"; then
    local current_date=$(date '+%Y-%m-%d %H:%M:%S')
    mv "$(pwd)/generated_clive_data/$BATS_TEST_NAME" "$(pwd)/generated_clive_data/$BATS_TEST_NAME.$current_date"
  fi
  : ${CLIVE_DATA_PATH:=$(pwd)/generated_clive_data/$BATS_TEST_NAME/.clive}
  export CLIVE_DATA_PATH="$CLIVE_DATA_PATH"
  : ${DATADIR:=$(pwd)/generated_clive_data/$BATS_TEST_NAME/.hived}
  export DATADIR="$DATADIR"
  : ${BLOCK_LOG_SOURCE:=$(pwd)/testnet_block_log/blockchain/block_log}
  export BLOCK_LOG_SOURCE="$BLOCK_LOG_SOURCE"
  : ${CONFIG_INI_SOURCE:=$(pwd)/testnet_block_log/config.ini}
  export CONFIG_INI_SOURCE="$CONFIG_INI_SOURCE"

  "$CLIVE_BEEKEEPER__PATH" --version >> /dev/null
  "$HIVED_PATH" --version | grep testnet >> /dev/null

  run "${BATS_TEST_DIRNAME}/common/run_hived.sh" "$DATADIR" "$BLOCK_LOG_SOURCE" "$CONFIG_INI_SOURCE"
  [ "$status" -eq 0 ]

  export CLIVE_SECRETS__DEFAULT_KEY="5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYik"
  export CLIVE_SECRETS__NODE_ADDRESS="http://127.0.0.1:8090"
  export CLIVE_NODE__CHAIN_ID="18dcf0a285365fc58b71f18b3d3fec954aa0c141c44e4e5cb4cf777b9eab274e"
}

teardown() {
  run "${BATS_TEST_DIRNAME}/common/stop_hived.sh" "$DATADIR" "$BLOCK_LOG_SOURCE" "$CONFIG_INI_SOURCE"
  [ "$status" -eq 0 ]
}


@test "example test" {
  run "${BATS_TEST_DIRNAME}/example/example.sh"
  echo "status: ${status}"
  echo "output: ${output}"
  [ "$status" -eq 0 ]
}

@test "show pending withdrawals" {
  run "${BATS_TEST_DIRNAME}/savings/show_pending_withdrawals.sh"
  echo "status: ${status}"
  echo "output: ${output}"
  [ "$status" -eq 0 ]
}

@test "process savings deposit" {
  echo "$CLIVE_DATA_PATH"
  python3 -c "from clive.__private.config import settings; print(settings.data_path)"
  run "${BATS_TEST_DIRNAME}/savings/process_savings_deposit.sh"
  echo "status: ${status}"
  echo "output: ${output}"
  [ "$status" -eq 0 ]
}

@test "process savings withdrawal" {
  echo "$CLIVE_DATA_PATH"
  python3 -c "from clive.__private.config import settings; print(settings.data_path)"
  run "${BATS_TEST_DIRNAME}/savings/process_savings_withdrawal.sh"
  echo "status: ${status}"
  echo "output: ${output}"
  [ "$status" -eq 0 ]
}

@test "process savings withdrawal cancel" {
  echo "$CLIVE_DATA_PATH"
  python3 -c "from clive.__private.config import settings; print(settings.data_path)"
  run "${BATS_TEST_DIRNAME}/savings/process_savings_withdrawal_cancel.sh"
  echo "status: ${status}"
  echo "output: ${output}"
  [ "$status" -eq 0 ]
}
