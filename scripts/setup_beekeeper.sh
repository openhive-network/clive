#!/bin/bash

cleanup() {
  echo "Performing cleanup...."
  clive beekeeper close
  echo "Cleanup actions done."
}
trap cleanup HUP INT QUIT TERM
trap cleanup EXIT


clive --install-completion >/dev/null 2>&1
output=$(clive-dev beekeeper spawn) # Spawn the beekeeper so commands that require it don't have to do it every time

BEEKEEPER_HTTP_ENDPOINT=$(echo "$output" | tail -2 | head -1)
CLIVE_BEEKEEPER__SESSION_TOKEN=$(echo "$output" | tail -1)


read -srp "enter profile name: " CLIVE_PROFILE_NAME
echo
read -srp "enter profile password: " CLIVE_PASSWORD
echo

clive beekeeper unlock --profile-name "$CLIVE_PROFILE_NAME" --password "$CLIVE_PASSWORD" --http-endpoint "$BEEKEEPER_HTTP_ENDPOINT" --session-token "$CLIVE_BEEKEEPER__SESSION_TOKEN"
