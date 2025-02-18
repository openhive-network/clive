#!/bin/bash

set -euo pipefail

function find_password_private_keys() {
     local exclude_patterns=(
        "Error in response from url"
        "Problem occurred during communication with"
        "CI_"
    )

    find . -path "*/clive/*/latest.log" -print0 |
    xargs -0 \
    grep --with-filename --line-number --ignore-case --word-regexp  --extended-regexp \
        '(pass(word)?|[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{51})' |
    grep --invert-match --extended-regexp "$(IFS='|'; echo "${exclude_patterns[*]}")" || true
}

amount_of_occurrences=$(find_password_private_keys --count)
if [[ $amount_of_occurrences -ne 0 ]]; then
    echo "Error: Found ${amount_of_occurrences} occurrences of private key or password"
    find_password_private_keys 2>&1
    exit "${amount_of_occurrences}"
fi;

echo "Ok: No sensitive data found in clive logs."
exit 0
