#!/bin/bash

function find_password_private_keys() {
    grep \
        --include="latest.log*" \
        -r -i -w  -E '(pass(word)?|[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{51})' |
        grep "$@" -v -E '(Error in response from url|Problem occurred during communication with|test_tools.__private.logger)'
}

amount_of_occurences=$(find_password_private_keys -c)
if [[ $amount_of_occurences -ne 0 ]]; then
    echo "Error! Found $amount_of_occurences occurrences of private key or password"
    find_password_private_keys 2>&1
fi;
exit $amount_of_occurences
