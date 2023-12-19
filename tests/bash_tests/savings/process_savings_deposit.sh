#!/usr/bin/env bash

set -xeuo pipefail

clive show profiles
clive configure profile add  --profile-name=alice --password=alice
clive configure working-account add --account-name=alice
clive configure key add --key=5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYik --password=alice --alias=alice@active
clive show profiles

clive show balances
clive process savings deposit --amount="1 HIVE" --password=alice --sign=alice@active
clive show balances
