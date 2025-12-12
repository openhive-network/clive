# syntax=registry.gitlab.syncad.com/hive/common-ci-configuration/dockerfile:1.5
ARG HIVED_IMAGE

ARG PYTHON_INSTALLER_IMAGE

ARG BASE_IMAGE

ARG CI_REGISTRY_IMAGE=registry.gitlab.syncad.com/hive/clive/

FROM $HIVED_IMAGE AS hived_image

FROM $BASE_IMAGE AS preconfigured_base_image

ARG CLIVE_VERSION
ENV CLIVE_VERSION=${CLIVE_VERSION}

ARG CLIVE_UID=2001
ENV CLIVE_UID=${CLIVE_UID}

ENV APT_CACHE_DIR=/var/cache/buildkit/apt
ENV PIP_CACHE_DIR=/var/cache/buildkit/pip

# create and use python virtualenv (use directory outside clive user home to reduce usermod execution time)
ENV PYTHON_VENV_PATH="/python_venv"
ENV PATH="${PYTHON_VENV_PATH}/bin:$PATH" VIRTUAL_ENV=${PYTHON_VENV_PATH}

RUN --mount=type=cache,mode=0777,sharing=locked,target=${APT_CACHE_DIR} \
    useradd -o -d /clive -ms /bin/bash -u ${CLIVE_UID} -g users -c "clive application account" "clive" && \
    mkdir -p /clive && mkdir -vp "${PYTHON_VENV_PATH}" && \
    chown -R clive:users /clive && \
    chmod -R g+w /clive && \
    chown -R clive:users "${PYTHON_VENV_PATH}" && \
    chmod -R g+w "${PYTHON_VENV_PATH}" && \
    chown -R clive:users /var/cache/ && \
    chmod -R 777 /var/cache/

USER clive

SHELL ["/bin/bash", "-c"]

COPY ./docker/entrypoint.sh .
RUN mkdir /clive/scripts
COPY --chown=clive ./scripts/activate_beekeeper.sh /clive/scripts/

COPY --chown=clive ./pyproject.toml /clive/
COPY --chown=clive ./poetry.lock /clive/
COPY --chown=clive ./README.md /clive/

WORKDIR /clive

# crucial for proper display
ENV COLORTERM=truecolor

FROM $PYTHON_INSTALLER_IMAGE AS python_installer

ARG CLIVE_VERSION
ENV CLIVE_VERSION=${CLIVE_VERSION}

ARG CLIVE_UID=2001
ENV CLIVE_UID=${CLIVE_UID}

ENV APT_CACHE_DIR=/var/cache/buildkit/apt
ENV PIP_CACHE_DIR=/var/cache/buildkit/pip

# create and use python virtualenv (use directory outside clive user home to reduce usermod execution time)
ENV PYTHON_VENV_PATH="/python_venv"
ENV PATH="${PYTHON_VENV_PATH}/bin:$PATH" VIRTUAL_ENV=${PYTHON_VENV_PATH}

RUN --mount=type=cache,mode=0777,sharing=locked,target=${APT_CACHE_DIR} \
    useradd -o -d /clive -ms /bin/bash -u ${CLIVE_UID} -g users -c "clive application account" "clive" && \
    mkdir -p /clive && mkdir -vp "${PYTHON_VENV_PATH}" && \
    chown -R clive:users /clive && \
    chmod -R g+w /clive && \
    chown -R clive:users "${PYTHON_VENV_PATH}" && \
    chmod -R g+w "${PYTHON_VENV_PATH}" && \
    chown -R clive:users /var/cache/ && \
    chmod -R 777 /var/cache/

USER clive
WORKDIR /clive

SHELL ["/bin/bash", "-c"]

# Project IDS:
# - 198 -> hive (generated APIs)
# - 362 -> schemas
# - 392 -> clive
# - 419 -> wax
# - 434 -> beekeepy
RUN --mount=type=cache,mode=0777,uid=${CLIVE_UID},target=${PIP_CACHE_DIR} \
    source /python_venv/bin/activate && \
    pip install hiveio_clive=="${CLIVE_VERSION}" \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/198/packages/pypi/simple \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/362/packages/pypi/simple \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/393/packages/pypi/simple \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/419/packages/pypi/simple \
    --extra-index-url https://gitlab.syncad.com/api/v4/projects/434/packages/pypi/simple && \
    # Remove the cache so it is not included in the image to save space, but grant group write access so the clive user can generate it itself.
    find "${PYTHON_VENV_PATH}" -name __pycache__ -exec rm -rf {} + && \
    chmod -R g+w "${PYTHON_VENV_PATH}"


FROM preconfigured_base_image AS instance

ARG BUILD_TIME
ARG GIT_COMMIT_SHA
ARG GIT_CURRENT_BRANCH
ARG GIT_LAST_LOG_MESSAGE
ARG GIT_LAST_COMMITTER
ARG GIT_LAST_COMMIT_DATE

COPY --chown=clive --from=python_installer "${PYTHON_VENV_PATH}" "${PYTHON_VENV_PATH}"

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

USER root
ENTRYPOINT ["/entrypoint.sh"]

# this target should be built using a testnet hived image as a base (to have embedded testnet)
FROM instance AS embedded_testnet_instance

ENV HIVED_BINARIES_DIR_SOURCE="/home/hived/bin"
ENV HIVED_BINARIES_DIR_DEST="${HIVED_BINARIES_DIR_SOURCE}/"

# Copy all the required executables from hived image
COPY --chown=clive --from=hived_image "${HIVED_BINARIES_DIR_SOURCE}/hived" "${HIVED_BINARIES_DIR_SOURCE}/get_dev_key" "${HIVED_BINARIES_DIR_SOURCE}/block_log_util" \
  "${HIVED_BINARIES_DIR_DEST}"

RUN strip -s "${HIVED_BINARIES_DIR_DEST}"/*

# Installing faketime lib, because it is needed in embedded testnet.
# The Faketime library is used in embedded testnet images to start blockchain nodes
# with the correct historical timestamp matching the generated block_log.
# Based on https://gitlab.syncad.com/hive/hive/blob/2a04c2be5d4b47c38ab498e588465bf041d294d6/scripts/setup_ubuntu.sh#L70
RUN git clone --depth 1 --branch bw_timer_settime_fix https://gitlab.syncad.com/bwrona/faketime.git && \
    pushd faketime && CFLAGS="-O2 -DFAKE_STATELESS=1" make && \
    sudo make install && \
    popd && \
    rm -rf faketime

ARG CLIVE_SECRETS__DEFAULT_PRIVATE_KEY="5KTNAYSHVzhnVPrwHpKhc5QqNQt6aW8JsrMT7T4hyrKydzYvYik"
ENV CLIVE_SECRETS__DEFAULT_PRIVATE_KEY=${CLIVE_SECRETS__DEFAULT_PRIVATE_KEY}

ARG CLIVE_SECRETS__NODE_ADDRESS="http://127.0.0.1:8090"
ENV CLIVE_SECRETS__NODE_ADDRESS=${CLIVE_SECRETS__NODE_ADDRESS}

ARG CLIVE_NODE__CHAIN_ID="18dcf0a285365fc58b71f18b3d3fec954aa0c141c44e4e5cb4cf777b9eab274e"
ENV CLIVE_NODE__CHAIN_ID=${CLIVE_NODE__CHAIN_ID}

# Paths to executables required for test-tools
ENV HIVED_PATH="${HIVED_BINARIES_DIR_DEST}/hived"
ENV GET_DEV_KEY_PATH="${HIVED_BINARIES_DIR_DEST}/get_dev_key"
ENV BLOCK_LOG_UTIL_PATH="${HIVED_BINARIES_DIR_DEST}/block_log_util"

# Get all the files required for embedded testnet
COPY --chown=clive ./testnet_node.py /clive

ENV TEST_TOOLS_PATH="hive/tests/python/hive-local-tools/test-tools/"
COPY --chown=clive ${TEST_TOOLS_PATH} /clive/${TEST_TOOLS_PATH}

ENV LOCAL_TOOLS_PATH="tests/clive-local-tools/"
COPY --chown=clive ${LOCAL_TOOLS_PATH} /clive/${LOCAL_TOOLS_PATH}

COPY --from=python_installer /poetry_venv /poetry_venv

ENV PATH="/home/hived_admin/.local/bin:/poetry_venv/bin:$PATH"

# Run dev installation to supplement with embeddedtestnet dependencies
RUN set -ex; source "${PYTHON_VENV_PATH}/bin/activate" && \
    poetry install --only embeddedtestnet --no-root

ENV TESTNET_MODE=1

LABEL org.opencontainers.image.ref.name="Clive+Testnet"
LABEL org.opencontainers.image.title="Clive with Testnet Image"
LABEL org.opencontainers.image.description="Runs Clive with embedded Hive Testnet"

USER root
ENTRYPOINT ["/entrypoint.sh"]
