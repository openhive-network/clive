ARG BEEKEEPER_IMAGE
ARG BASE_IMAGE

ARG CI_REGISTRY_IMAGE=registry.gitlab.syncad.com/hive/clive/


FROM $BEEKEEPER_IMAGE as beekeper_source


FROM $BASE_IMAGE AS common

SHELL ["/bin/bash", "-c"]

ADD --chown=hived_admin:users ./docker/entrypoint.sh .

ADD --chown=hived_admin:users ./pyproject.toml /clive/
ADD --chown=hived_admin:users ./poetry.lock /clive/
ADD --chown=hived_admin:users ./README.md /clive/

WORKDIR /clive

ENV BEEKEEPER_PATH="/clive/beekeeper"
COPY --from=beekeper_source --chown=hived_admin:users "/home/hived/bin/beekeeper" "${BEEKEEPER_PATH}"

# crucial for proper display
ENV COLORTERM=truecolor

# libboost-all-dev is required for wax
RUN sudo apt-get update && \
    sudo apt-get install -y python3-venv libboost-all-dev && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/*

# create and use python virtualenv
ENV PYTHON_VENV_PATH="/clive/venv"
RUN python3 -m venv ${PYTHON_VENV_PATH}
ENV PATH="${PYTHON_VENV_PATH}/bin:$PATH" VIRTUAL_ENV=${PYTHON_VENV_PATH}


FROM common as instance

ARG CLIVE_VERSION

# Project IDS:
# - 362 -> schemas
# - 392 -> clive
# - 419 -> wax
RUN pip install clive=="${CLIVE_VERSION}" \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/362/packages/pypi/simple \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/393/packages/pypi/simple \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/419/packages/pypi/simple

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

# Get all the files required for embedded testnet
ADD --chown=hived_admin:users ./testnet_node.py /clive

ENV LOCAL_TOOLS_PATH="tests/clive-local-tools/"
ADD --chown=hived_admin:users ${LOCAL_TOOLS_PATH} /clive/${LOCAL_TOOLS_PATH}

ENV TEST_TOOLS_PATH="hive/tests/python/hive-local-tools/test-tools/"
ADD --chown=hived_admin:users ${TEST_TOOLS_PATH} /clive/${TEST_TOOLS_PATH}

RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.7.0
ENV PATH="/home/hived_admin/.local/bin:$PATH"

# Run dev installation to supplement with development dependencies
RUN poetry install --no-root

ENV TESTNET_MODE=1

ENTRYPOINT ["/home/hived_admin/entrypoint.sh"]
