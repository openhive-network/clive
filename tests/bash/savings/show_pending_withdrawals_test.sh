#!/usr/bin/env bash

set -xeuo pipefail

clive show profiles
clive configure profile add  --profile-name=alice --password=alice
clive configure working-account add --account-name=alice
clive show profiles

clive show pending withdrawals
