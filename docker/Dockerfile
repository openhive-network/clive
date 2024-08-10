ARG HIVED_IMAGE
ARG BASE_IMAGE

ARG CI_REGISTRY_IMAGE=registry.gitlab.syncad.com/hive/clive/


FROM $HIVED_IMAGE AS hived_image

FROM registry.gitlab.syncad.com/hive/hive/ci-base-image:ubuntu22.04-10 AS stripped_beekeeper_source

COPY --from=hived_image "/home/hived/bin/beekeeper" "/home/hived/bin/beekeeper"
RUN strip -p /home/hived/bin/beekeeper -o /home/hived_admin/beekeeper.stripped

FROM $BASE_IMAGE AS common

SHELL ["/bin/bash", "-c"]

ADD ./docker/entrypoint.sh .

ADD ./pyproject.toml /clive/
ADD ./poetry.lock /clive/
ADD ./README.md /clive/

WORKDIR /clive

ENV BEEKEEPER_PATH_SOURCE="/home/hived_admin/beekeeper.stripped"
ENV BEEKEEPER_PATH_DEST="/clive/beekeeper"
COPY --from=stripped_beekeeper_source "${BEEKEEPER_PATH_SOURCE}" "${BEEKEEPER_PATH_DEST}"

# crucial for proper display
ENV COLORTERM=truecolor

RUN apt-get update && \
    apt-get install -y python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# create and use python virtualenv
ENV PYTHON_VENV_PATH="/clive/venv"
RUN python3 -m venv ${PYTHON_VENV_PATH}
ENV PATH="${PYTHON_VENV_PATH}/bin:$PATH" VIRTUAL_ENV=${PYTHON_VENV_PATH}


FROM common AS instance

ARG CLIVE_VERSION

ARG BUILD_TIME
ARG GIT_COMMIT_SHA
ARG GIT_CURRENT_BRANCH
ARG GIT_LAST_LOG_MESSAGE
ARG GIT_LAST_COMMITTER
ARG GIT_LAST_COMMIT_DATE

# Project IDS:
# - 362 -> schemas
# - 392 -> clive
# - 419 -> wax
RUN pip install clive=="${CLIVE_VERSION}" \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/362/packages/pypi/simple \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/393/packages/pypi/simple \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/419/packages/pypi/simple

ENV TESTNET_MODE=0

LABEL org.opencontainers.image.created="$BUILD_TIME"
LABEL org.opencontainers.image.url="https://hive.io/"
LABEL org.opencontainers.image.documentation="https://gitlab.syncad.com/hive/clive"
LABEL org.opencontainers.image.source="https://gitlab.syncad.com/hive/clive"
LABEL org.opencontainers.image.version="${CLIVE_VERSION}"
LABEL org.opencontainers.image.revision="$GIT_COMMIT_SHA"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.ref.name="Clive"
LABEL org.opencontainers.image.title="Clive Image"
LABEL org.opencontainers.image.description="Runs Clive application"
LABEL io.hive.image.branch="$GIT_CURRENT_BRANCH"
LABEL io.hive.image.commit.log_message="$GIT_LAST_LOG_MESSAGE"
LABEL io.hive.image.commit.author="$GIT_LAST_COMMITTER"
LABEL io.hive.image.commit.date="$GIT_LAST_COMMIT_DATE"

ENTRYPOINT ["/entrypoint.sh"]


# this target should be built using a testnet hived image as a base (to have embedded testnet)
FROM instance AS embedded_testnet_instance

ENV HIVED_BINARIES_DIR_SOURCE="/home/hived/bin"
ENV HIVED_BINARIES_DIR_DEST=${HIVED_BINARIES_DIR_SOURCE}

# Copy all the required executables from hived image
COPY --from=hived_image "${HIVED_BINARIES_DIR_SOURCE}" "${HIVED_BINARIES_DIR_DEST}"

ARG CLIVE_SECRETS__DEFAULT_PRIVATE_KEY="5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYik"
ENV CLIVE_SECRETS__DEFAULT_PRIVATE_KEY=${CLIVE_SECRETS__DEFAULT_PRIVATE_KEY}

ARG CLIVE_SECRETS__NODE_ADDRESS="http://127.0.0.1:8090"
ENV CLIVE_SECRETS__NODE_ADDRESS=${CLIVE_SECRETS__NODE_ADDRESS}

ARG CLIVE_NODE__CHAIN_ID="18dcf0a285365fc58b71f18b3d3fec954aa0c141c44e4e5cb4cf777b9eab274e"
ENV CLIVE_NODE__CHAIN_ID=${CLIVE_NODE__CHAIN_ID}

# Paths to executables required for test-tools
ENV HIVED_PATH="${HIVED_BINARIES_DIR_DEST}/hived"
ENV CLI_WALLET_PATH="${HIVED_BINARIES_DIR_DEST}/cli_wallet"
ENV GET_DEV_KEY_PATH="${HIVED_BINARIES_DIR_DEST}/get_dev_key"
ENV COMPRESS_BLOCK_LOG_PATH="${HIVED_BINARIES_DIR_DEST}/compress_block_log"

# Get all the files required for embedded testnet
ADD ./testnet_node.py /clive

ENV TEST_TOOLS_PATH="hive/tests/python/hive-local-tools/test-tools/"
ADD ${TEST_TOOLS_PATH} /clive/${TEST_TOOLS_PATH}

ENV LOCAL_TOOLS_PATH="tests/clive-local-tools/"
ADD ${LOCAL_TOOLS_PATH} /clive/${LOCAL_TOOLS_PATH}

RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.7.0
ENV PATH="/home/hived_admin/.local/bin:$PATH"

# Run dev installation to supplement with embeddedtestnet dependencies
RUN poetry install --only embeddedtestnet --no-root

ENV TESTNET_MODE=1

LABEL org.opencontainers.image.ref.name="Clive+Testnet"
LABEL org.opencontainers.image.title="Clive with Testnet Image"
LABEL org.opencontainers.image.description="Runs Clive with embedded Hive Testnet"

ENTRYPOINT ["/entrypoint.sh"]
