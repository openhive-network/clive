#!/bin/bash

set -euo pipefail

count=$(pgrep "beekeeper" --count || true)

if [[ $count -gt 0 ]]; then
    echo "Error: There is ${count} dangling 'beekeeper' process left."
    exit 2
fi

echo "Ok: No dangling 'beekeeper' process left."
exit 0
