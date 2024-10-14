#!/bin/bash

# Exit immediately on error, unset variables are errors, and fail on any command in a pipeline
set -euo pipefail

SCRIPTPATH="$(cd -- "$(dirname "$0")" >/dev/null 2>&1 && pwd -P)"
TESTNET_NODE_LOG_FILE="testnet_node.log"
INTERACTIVE_CLI_MODE=0
BEEKEEPER_ALREADY_CLOSED=0

trap "clean_up" SIGTERM SIGINT SIGQUIT SIGHUP EXIT

# Clean after termination of shell
clean_up() {
  close_beekeeper
}

# Start Beekeeper with prepared session token
start_beekeeper_with_prepared_session_token() {
  echo "Starting beekeeper with prepared session token"
  output=$(clive beekeeper spawn)
  BEEKEEPER_HTTP_ENDPOINT=$(echo "$output" | grep -oE 'http://[0-9.]+:[0-9]+')

  CLIVE_BEEKEEPER__SESSION_TOKEN=$(curl -s --data '{
    "jsonrpc": "2.0",
    "method": "beekeeper_api.create_session",
    "params": {
      "salt": "clive-cli-session",
      "notifications_endpoint": "'"${BEEKEEPER_HTTP_ENDPOINT}"'"
    },
    "id": 1
  }' "${BEEKEEPER_HTTP_ENDPOINT}" | jq .result.token | tr -d '"')


  if [[ "${CLIVE_BEEKEEPER__SESSION_TOKEN}" == "null" ]]; then
    echo "Error: There is no valid token."
    exit 1
  fi

  export CLIVE_BEEKEEPER__SESSION_TOKEN=${CLIVE_BEEKEEPER__SESSION_TOKEN}
  export BEEKEEPER_HTTP_ENDPOINT=${BEEKEEPER_HTTP_ENDPOINT}

  echo "Beekeeper session token: ${CLIVE_BEEKEEPER__SESSION_TOKEN}"
  echo "Beekeeper address : ${BEEKEEPER_HTTP_ENDPOINT}"
}

# Close beekeeper
close_beekeeper() {
  if [[ ${BEEKEEPER_ALREADY_CLOSED} -eq 0 ]]; then
    echo "Closing beekeeper : ${BEEKEEPER_HTTP_ENDPOINT}"
    clive beekeeper close
    BEEKEEPER_ALREADY_CLOSED=1
  fi
}

# Unlock wallet for selected profile
unlock_wallet() {
  read -rsp "Enter password for profile ${SELECTED_PROFILE}: " password
  echo
  password="${password//$'\n'/}"
  response=$(curl -s --data '{
    "jsonrpc": "2.0",
    "method": "beekeeper_api.unlock",
    "params": {
      "token": "'"${CLIVE_BEEKEEPER__SESSION_TOKEN}"'",
      "wallet_name": "'"${SELECTED_PROFILE}"'",
      "password": "'"${password}"'"
    },
    "id": 1
  }' "${BEEKEEPER_HTTP_ENDPOINT}")

  error=$(echo "${response}" | jq .error)
  if [[ "${error}" != "null" ]]; then
    error_message=$(echo "${error}" | jq .message)
    echo "Error: ${error_message}."
    exit 1
  fi
}

# Print info about how to create profile
how_to_create_profile() {
  echo ""
  echo "If you want to create profile, please do the following."
  echo "clive configure profile add --profile-name PROFILE_NAME --password PROFILE_PASSWORD"
  echo ""
}

# Select one of the existing profiles
select_profile(){
  output=$(clive show profiles)
  profiles=$(echo "$output" | grep -oP "\[\K[^\]]+")
  IFS=',' read -ra profile_array <<< "$profiles"

  if [ ${#profile_array[@]} -eq 0 ]; then
    echo "There are no profiles."
    how_to_create_profile
  else
    echo "Select profile:"
    for i in "${!profile_array[@]}"; do
      profile=$(echo "${profile_array[i]}" | tr -d "' ")
      echo "$((i + 1)). $profile"
    done

    echo "$(( ${#profile_array[@]} + 1 )). create new profile"

    read -rp "Enter the number: " choice

    if [[ $choice -ge 1 && $choice -le ${#profile_array[@]} ]]; then
      selected_profile=$(echo "${profile_array[$((choice - 1))]}" | tr -d "' ")
      echo "You selected: $selected_profile"
      SELECTED_PROFILE=${selected_profile}
      echo "Selected profile is ${SELECTED_PROFILE}"
      unlock_wallet
    elif [[ $choice -eq $(( ${#profile_array[@]} + 1 )) ]]; then
      echo "You selected: create new profile"
      how_to_create_profile
    else
      echo "Error: Invalid selection!"
      exit 1
    fi
  fi
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

# Execute a script passed as an argument
execute_passed_script() {
  if [[ -n "${FILE_TO_EXECUTE:-}" ]]; then
    if [[ -f "${FILE_TO_EXECUTE}" ]]; then
      echo "Executing file: ${FILE_TO_EXECUTE}"
      # shellcheck disable=SC1090
      source "${FILE_TO_EXECUTE}"
    else
      echo "Error: ${FILE_TO_EXECUTE} does not exist or is not a file."
      exit 1
    fi
  fi
}

# Run shell with prepared Clive
run_clive() {
  clive --install-completion >/dev/null 2>&1
  bash
}

# Launch Clive in CLI mode
launch_cli() {
  start_beekeeper_with_prepared_session_token
  select_profile
  execute_passed_script
  run_clive
  close_beekeeper
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
    python3 testnet_node.py -p >${TESTNET_NODE_LOG_FILE} 2>&1 &
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
