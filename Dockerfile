FROM registry.gitlab.syncad.com/hive/hive/ci-base-image:ubuntu22.04-3

ADD --chown=hived_admin:users . /clive
WORKDIR /clive

ARG BEEKEEPER_LOCATION="./beekeeper"
ENV BEEKEEPER_PATH="/clive/beekeeper"
ADD --chown=hived_admin:users "${BEEKEEPER_LOCATION}" "${BEEKEEPER_PATH}"

RUN poetry self update

RUN poetry install --only main

# crucial for proper display
ENV COLORTERM=truecolor

ENTRYPOINT ["poetry", "run", "clive"]
