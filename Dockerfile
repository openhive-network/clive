FROM registry.gitlab.syncad.com/hive/clive/ci-base-image@sha256:62a6bfd24f898d47be5853e6a777021ba03f35ae951a7804b8a5a660816501ba

ADD . /clive
WORKDIR /clive

RUN poetry self update

RUN poetry install --no-dev

ENTRYPOINT ["poetry", "run", "clive"]
