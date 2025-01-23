#!/bin/bash

BEEKEEPER_ALREADY_CLOSED=0
trap "clean_up" SIGTERM SIGQUIT SIGHUP EXIT

# Start Beekeeper with prepared session token
start_beekeeper_with_prepared_session_token() {
  CLIVE_BEEKEEPER__REMOTE_ADDRESS=$(clive beekeeper spawn --echo-address-only)
  export CLIVE_BEEKEEPER__REMOTE_ADDRESS
  # shellcheck disable=SC2181
  if [[ $? -ne 0 ]]; then
    echo "Error: Fail to spawn Beekeeper. Aborting..."
    exit 1
  fi

  CLIVE_BEEKEEPER__SESSION_TOKEN=$(clive beekeeper create-session --echo-token-only)
  export CLIVE_BEEKEEPER__SESSION_TOKEN
  # shellcheck disable=SC2181
  if [[ $? -ne 0 ]]; then
    echo "Error: Failed to create a new beekeeper session. Aborting..."
    exit 1
  fi
}

# Unlock wallet for selected profile
unlock_wallet() {
  local profile_name_arg=""
  if [[ -n "$SELECTED_PROFILE" ]]; then
    profile_name_arg="--profile-name=${SELECTED_PROFILE}"
  fi
  # shellcheck disable=SC2086
  clive unlock $profile_name_arg --include-create-new-profile
  return $?
}

# Print info about how to create profile
how_to_create_profile() {
  echo ""
  echo "If you want to create profile, please do the following."
  echo "clive configure profile add --profile-name PROFILE_NAME --password PROFILE_PASSWORD"
  echo ""
}

# Execute a script passed as an argument
execute_passed_script() {
  if [[ -n "${FILE_TO_EXECUTE:-}" ]]; then
    if [[ -f "${FILE_TO_EXECUTE}" ]]; then
      echo "Executing file: ${FILE_TO_EXECUTE}"
      # shellcheck disable=SC1090
      source "${FILE_TO_EXECUTE}"
      exit 0
    else
      echo "Error: ${FILE_TO_EXECUTE} does not exist or is not a file."
      exit 1
    fi
  fi
}


close_beekeeper() {
  if [[ ${BEEKEEPER_ALREADY_CLOSED} -eq 0 ]]; then
    clive beekeeper close >/dev/null 2>&1
    BEEKEEPER_ALREADY_CLOSED=1
  fi
}


# Execute before entering interactive mode
setup() {
  start_beekeeper_with_prepared_session_token
  if ! unlock_wallet; then
    echo "Error: Failed to unlock wallet. Aborting..."
    exit 1
  fi
  execute_passed_script
  # shellcheck disable=SC1090
  source ~/.bashrc
}

# Clean after termination of shell
clean_up() {
  trap '' SIGINT
  echo "Please wait. Cleaning up..."
  close_beekeeper
  trap - SIGINT
}

setup
