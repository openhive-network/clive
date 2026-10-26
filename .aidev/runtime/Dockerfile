# The image AIDEV runs this project's suites in (`environment.image` in
# .aidev/project.yaml). Suites run with `--network none` and the caller's uid, so
# everything they need is in the image:
#
# * common-ci-configuration's python-test-tools (Ubuntu 26.04, Python 3.14,
#   poetry 2.1.3), the tool image CI's python templates use;
# * the TESTNET hived, cli_wallet, get_dev_key and block_log_util from hive's testnet
#   image, as CI's prepare_testnet_hived_image extracts them (`/home/hived/bin`).
#   HIVED_PATH, CLI_WALLET_PATH, GET_DEV_KEY_PATH and BLOCK_LOG_UTIL_PATH are the
#   variables CI's .testing sets for test-tools; the tag is what CI's
#   find_testnet_hived_image picks for HIVED_BRANCH, pinned by digest (re-pin: see
#   .aidev/README.md). The MAINNET beekeeper clive and test-tools run is the one the
#   hiveio-beekeepy wheel ships (beekeepy/beekeeper, the only place
#   beekeepy looks), so poetry.lock pins it; hive's mainnet image no longer carries a
#   beekeeper, and CI's BEEKEEPER_BINARY is read by nothing;
# * libfaketime (below), which test-tools needs to start a node, built in its own
#   stage so no compiler reaches the image (every locked package has a cp314 wheel);
# * node, for .aidev/junit-helpers.sh, and git;
# * poetry.lock's main, dev, static-analysis and embeddedtestnet groups in /opt/py
#   (pytest + xdist/timeout/asyncio/cov, test-tools, ruff, mypy), installed by poetry from
#   a copy at /work so the editable clive-local-tools path dependency resolves to the
#   mounted workspace (/work/tests/clive-local-tools); clive itself (`--no-root`) is
#   importable from /work through a .pth, and its [project.scripts] entry points
#   (`clive`, `clive-dev`, which test_startup/test_signals run) are written as
#   wrappers in /opt/py/bin, since `--no-root` installs none.
#
# Build and pin it with .aidev/runtime/build.sh; see .aidev/README.md.

# libfaketime, which test-tools preloads into hived (/usr/local/lib/faketime): the
# Syncad fork common-ci-configuration's ci-base-image builds, at a pinned commit of
# its bw_timer_settime_fix branch, with the same flags.
FROM registry.gitlab.syncad.com/hive/common-ci-configuration/python-test-tools@sha256:6f7fb3acf0c4f5551cf9fa58a382fbae66c9c47b06510b31685553581ef1409e AS faketime
USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git gcc make libc6-dev \
    && git init -q /tmp/faketime && cd /tmp/faketime \
    && git fetch -q --depth 1 https://gitlab.syncad.com/hive/faketime.git 873b0941a3ed733e5a9bbd2929ff647cc5c61bbe \
    && git checkout -q FETCH_HEAD \
    && CFLAGS="-O2 -DFAKE_STATELESS=1" make \
    && make install \
    && test -f /usr/local/lib/faketime/libfaketimeMT.so.1

FROM registry.gitlab.syncad.com/hive/common-ci-configuration/python-test-tools@sha256:6f7fb3acf0c4f5551cf9fa58a382fbae66c9c47b06510b31685553581ef1409e

USER root

ENV HOME=/tmp \
    PATH=/opt/py/bin:$PATH \
    VIRTUAL_ENV=/opt/py \
    HIVED_PATH=/opt/hived/testnet/hived \
    CLI_WALLET_PATH=/opt/hived/testnet/cli_wallet \
    GET_DEV_KEY_PATH=/opt/hived/testnet/get_dev_key \
    BLOCK_LOG_UTIL_PATH=/opt/hived/testnet/block_log_util \
    PYTHONDONTWRITEBYTECODE=1 \
    MYPY_CACHE_DIR=/tmp/.mypy_cache \
    RUFF_CACHE_DIR=/tmp/.ruff_cache

# hive testnet image 6509cbed (hive develop 6509cbed3ed7c3e60806ab15028dfd4adcda0bb9)
COPY --from=registry.gitlab.syncad.com/hive/hive/testnet@sha256:aaa77a3c4d37d06c848501d8d1154f321cd09047e3a8667960f9252a03964c1f \
     /home/hived/bin/ /opt/hived/testnet/
RUN cd /opt/hived/testnet && rm -rf CMakeFiles *.cmake *.h chain_test plugin_test
COPY --from=faketime /usr/local/lib/faketime/ /usr/local/lib/faketime/
COPY --from=faketime /usr/local/bin/faketime /usr/local/bin/faketime
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nodejs git \
    && rm -rf /var/lib/apt/lists/* \
    && chmod -R a+rX /opt/hived \
    && for b in "$HIVED_PATH" "$CLI_WALLET_PATH" "$GET_DEV_KEY_PATH" "$BLOCK_LOG_UTIL_PATH"; do \
         test -x "$b" || { echo "missing $b" >&2; exit 1; }; \
         if ldd "$b" | grep 'not found'; then echo "unresolved libraries in $b" >&2; exit 1; fi; \
       done \
    && "$HIVED_PATH" --version \
    && test -f /usr/local/lib/faketime/libfaketimeMT.so.1

COPY py/ /work/
RUN python3 -m venv --without-pip /opt/py \
    && cd /work \
    && POETRY_CACHE_DIR=/tmp/poetry-cache POETRY_VIRTUALENVS_CREATE=false poetry install --no-root --no-interaction \
         --with dev,static-analysis,embeddedtestnet --without docs \
    && /opt/py/bin/ruff --version && /opt/py/bin/mypy --version && /opt/py/bin/python -m pytest --version \
    && /opt/py/bin/python -c 'import pytest_cov' \
    && timeout 30 "$(/opt/py/bin/python -c 'import beekeepy, pathlib; print(pathlib.Path(beekeepy.__file__).parent)')/beekeeper" --version \
    && echo /work > "$(/opt/py/bin/python -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')/clive-workspace.pth" \
    && for ep in clive:clive.main clive-dev:clive.dev; do \
         printf '#!/opt/py/bin/python\nimport sys\nfrom %s import main\nsys.exit(main())\n' "${ep#*:}" > "/opt/py/bin/${ep%%:*}"; \
         chmod 755 "/opt/py/bin/${ep%%:*}"; \
       done \
    && rm -rf /work /tmp/poetry-cache /tmp/.cache /tmp/.config \
    && chmod -R a+rwX /opt/py
