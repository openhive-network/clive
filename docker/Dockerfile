ARG BEEKEEPER_IMAGE
ARG BASE_IMAGE

ARG CI_REGISTRY_IMAGE=registry.gitlab.syncad.com/hive/clive/

FROM $BEEKEEPER_IMAGE as beekeper_source

FROM $BASE_IMAGE AS instance

ADD --chown=hived_admin:users . /clive

WORKDIR /clive

ENV BEEKEEPER_PATH="/clive/beekeeper"
COPY --from=beekeper_source --chown=hived_admin:users "/home/hived/bin/beekeeper" "${BEEKEEPER_PATH}"

RUN poetry self update && \
    poetry install --only main

# crucial for proper display
ENV COLORTERM=truecolor

ENTRYPOINT ["poetry", "run", "clive"]
