FROM registry.gitlab.syncad.com/hive/hive/ci-base-image:ubuntu22.04-3

ADD . /clive
WORKDIR /clive

ARG BEEKEEPER_LOCATION
ADD ${BEEKEEPER_LOCATION} /clive/beekeeper

RUN poetry self update

RUN poetry install --only main

# crucial for proper display
ENV COLORTERM=truecolor

ENTRYPOINT ["poetry", "run", "clive"]
