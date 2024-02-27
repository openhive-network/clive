#!/bin/bash

count=$(pgrep "beekeeper" -c)

if [[ $count -gt 0 ]]; then
    echo "Error: There is dangling 'beekeeper' process left."
    exit 2
fi

echo "Ok: No dangling 'beekeeper' process left."
exit 0
