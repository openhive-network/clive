#!/bin/bash

function find_password_private_keys() {
    find . -path "*/clive/*/latest.log" -print0 |
    xargs -0 \
    grep --with-filename --line-number --ignore-case --word-regexp  --extended-regexp \
        '(pass(word)?|[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{51})' |
    grep "$@" --invert-match --extended-regexp \
        '(Error in response from url|Problem occurred during communication with|test_tools.__private.logger)'
}

amount_of_occurrences=$(find_password_private_keys --count)
if [[ $amount_of_occurrences -ne 0 ]]; then
    echo "Error! Found $amount_of_occurrences occurrences of private key or password"
    find_password_private_keys 2>&1
fi;
exit "$amount_of_occurrences"
