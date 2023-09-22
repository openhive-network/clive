ARG BEEKEEPER_IMAGE
ARG BASE_IMAGE

ARG CI_REGISTRY_IMAGE=registry.gitlab.syncad.com/hive/clive/

FROM $BEEKEEPER_IMAGE as beekeper_source

FROM $BASE_IMAGE AS instance

SHELL ["/bin/bash", "-c"]

ADD --chown=hived_admin:users ./docker/entrypoint.sh .
ADD --chown=hived_admin:users . /clive

WORKDIR /clive

ENV BEEKEEPER_PATH="/clive/beekeeper"
COPY --from=beekeper_source --chown=hived_admin:users "/home/hived/bin/beekeeper" "${BEEKEEPER_PATH}"

RUN poetry install --only main
RUN poetry dynamic-versioning  # Substitute versions because of https://github.com/mtkennerly/poetry-dynamic-versioning/issues/25#issuecomment-698193152, has to be done after installation otherwise pip will show "dirty" version

# crucial for proper display
ENV COLORTERM=truecolor

ENV TESTNET_MODE=0

ENTRYPOINT ["/home/hived_admin/entrypoint.sh"]

# this target should be built using a testnet hived image as a base (to have embedded testnet)
FROM instance as embedded_testnet_instance

ARG CLIVE_SECRETS__DEFAULT_KEY="5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYik"
ENV CLIVE_SECRETS__DEFAULT_KEY=${CLIVE_SECRETS__DEFAULT_KEY}

ARG CLIVE_SECRETS__NODE_ADDRESS="http://127.0.0.1:8090"
ENV CLIVE_SECRETS__NODE_ADDRESS=${CLIVE_SECRETS__NODE_ADDRESS}

ENV HIVED_PATH="/home/hived/bin/hived"
ENV CLI_WALLET_PATH="/home/hived/bin/cli_wallet"
ENV GET_DEV_KEY_PATH="/home/hived/bin/get_dev_key"
ENV COMPRESS_BLOCK_LOG_PATH="/home/hived/bin/compress_block_log"

WORKDIR /clive

# Run installation once again to supplement extras and development dependencies
RUN git restore pyproject.toml clive/__init__.py  # Restore files that were modified by previous dynamic-versioning
RUN poetry install
RUN poetry dynamic-versioning  # Substitute versions because of https://github.com/mtkennerly/poetry-dynamic-versioning/issues/25#issuecomment-698193152, has to be done after installation otherwise pip will show "dirty" version

ENV TESTNET_MODE=1

ENTRYPOINT ["/home/hived_admin/entrypoint.sh"]
