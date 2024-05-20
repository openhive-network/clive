#! /bin/bash
set -euo pipefail


if [ "$EUID" -ne 0 ]
then echo "Please run as root"
    exit 1
fi

apt-get update && apt-get install -y git build-essential && \
apt-get clean && rm -r /var/lib/apt/lists/*

git config --global --add safe.directory '*'

git clone --depth 1 --branch bw_timer_settime_fix https://gitlab.syncad.com/bwrona/faketime.git
pushd faketime && CFLAGS="-O2 -DFAKE_STATELESS=1" make
make install
popd
