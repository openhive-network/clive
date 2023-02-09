FROM registry.gitlab.syncad.com/hive/clive/ci-base-image@sha256:5bb28104ea74f8f2d1e6e3fd1fe860383a9ac72ba73eaa55bd14496b52fd7441

ADD . /clive
WORKDIR /clive

RUN poetry self update

RUN poetry install --no-dev

ENTRYPOINT ["poetry", "run", "clive"]
