#!/bin/bash

BEEKEEPER_ALREADY_CLOSED=0
trap "clean_up" SIGTERM SIGINT SIGQUIT SIGHUP EXIT


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
    echo "Closing beekeeper : ${BEEKEEPER_HTTP_ENDPOINT}"
    clive beekeeper close
    BEEKEEPER_ALREADY_CLOSED=1
  fi
}


# Execute before entering interactive mode
setup() {
  start_beekeeper_with_prepared_session_token
  select_profile
  execute_passed_script
}

# Clean after termination of shell
clean_up() {
  close_beekeeper
}

setup
