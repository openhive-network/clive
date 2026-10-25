# Automated contributions

This directory configures the automated development platform that contributes to this
repository. This note says which branches it uses here and how its work reaches the
project's main line.

## Branches

- `aidev/integration` — the integration branch. Automated work lands here and nowhere else.
- `develop` — the project's main line; reached from `aidev/integration` only by merge request (`aidev handoff`, a linear one-commit-per-change copy on `aidev/handoff`, since `develop` merges fast-forward only).
- `ai/*` — one branch per task, created and deleted by the platform. Do not commit to them.
- `session/*` — a session's accumulated work, landed on the integration branch as a batch.

## How work reaches the main line

Task and session branches never reach `aidev/integration` through merge requests; the platform
lands them after its own verification. `aidev/integration` reaches `develop` by this project's
usual process, merge requests included — the platform never merges into any other branch.

Whether this project's CI pipelines skip `ai/*` and `session/*` branches is decided by the
project's CI rules; maintainers record that decision here.

## Suites run before work lands

Declared in `.aidev/project.yaml` under `verification`, run by `.aidev/run-checks.sh` in the
test runtime image, offline (`--network none`), with pytest's junit per step in
`test-results/<suite>/`:

- `quick` — `unit`: `pytest -n 16 tests/unit`, timing tests left out
- `canary` — `functional`: CI's `testing_clive` selection (everything except
  `tests/functional/tui`, `tests/functional/cli`, the timing tests and `tests/unit/async_hived`)
- `baseline` — `unit`, `functional-cli` (`tests/functional/cli`, CI's `testing_cli`)
- `full` — `unit`, `functional-cli`, `functional`
- `static` — `ruff check`, `ruff format --check`, `mypy` on `clive/ tests/`, and
  `scripts/check_for_private_key_or_password_logging.bash` (it scans the clive logs test runs
  leave under `tests/`, so it only finds something after a test step ran in the same checkout)
- `coverage` — `unit` under `--cov=clive` (`coverage.xml`)
- `system` — `tui`: `tests/functional/tui` (CI's `testing_tui`)

`tests/unit/test_imports_times.py` and `tests/unit/test_command_execution_times.py` measure
wall time and fail under load; CI runs them alone (`testing_clive_times`, one process) and no
slot here runs them. `pre-commit` (prettier, stylelint, pydoclint, poetry-lock) and the
poetry-lock sanity/stability jobs need the network and are not reproduced.

## Test runtime

`.aidev/runtime/Dockerfile` builds on common-ci-configuration's `python-test-tools`
(Ubuntu 26.04, Python 3.14, poetry 2.1.3) and adds:

- poetry.lock's main, dev, static-analysis and embeddedtestnet groups in `/opt/py`
  (`--no-root`; clive and the editable `tests/clive-local-tools` resolve to the mounted
  workspace at `/work`), wrappers for the `clive` / `clive-dev` entry points
  (`tests/functional/test_startup.py` and `test_signals.py` run them); the dev group's
  pytest-cov serves the `coverage` step;
- libfaketime from the Syncad fork (`hive/faketime`, `bw_timer_settime_fix` at
  `873b0941a3ed733e5a9bbd2929ff647cc5c61bbe`), built as common-ci-configuration's
  ci-base-image builds it, in a separate build stage: every locked package has a Python 3.14
  wheel, so the image carries no compiler; test-tools preloads it into every node it starts;
- the TESTNET `hived`, `cli_wallet`, `get_dev_key`, `block_log_util` that CI's
  `prepare_testnet_hived_image` extracts from `/home/hived/bin`, copied from the digest-pinned
  `registry.gitlab.syncad.com/hive/hive/testnet` image into `/opt/hived/testnet/` and exposed to
  test-tools as `HIVED_PATH`, `CLI_WALLET_PATH`, `GET_DEV_KEY_PATH`, `BLOCK_LOG_UTIL_PATH` (the
  variables CI's `.testing` sets).

  Pinned at onboarding (2026-10-25): hive `develop` `6509cbed3ed7c3e60806ab15028dfd4adcda0bb9`
  (tag `6509cbed`, `blockchain_version` 1.29.0), digest
  `sha256:aaa77a3c4d37d06c848501d8d1154f321cd09047e3a8667960f9252a03964c1f`.

The MAINNET beekeeper clive and test-tools run is the binary the `hiveio-beekeepy` wheel ships
(`beekeepy/beekeeper`, the only place beekeepy looks for it), so `poetry.lock` pins
it. CI's `prepare_mainnet_hived_image` / `BEEKEEPER_BINARY` are not reproduced: nothing reads
`BEEKEEPER_BINARY`, and hive's mainnet image (`registry.gitlab.syncad.com/hive/hive:6509cbed`)
no longer carries a `beekeeper`.

### Re-pinning the hived binaries

CI follows hive: with `.hived_override_tag` `none` its `find_*_hived_image` jobs take the
newest image of `HIVED_BRANCH` (`develop`), otherwise `HIVED_OVERRIDE_TAG`. The image here
does not move by itself, so re-pin when CI's choice moves (a new `HIVED_OVERRIDE_TAG` in
`.gitlab-ci.yml`, or the testnet block log in `tests/` being regenerated for a newer hived):

1. Take the tag CI uses — the `HIVED_OVERRIDE_TAG`, or the `UPSTREAM_IMAGE=` line of the
   latest `find_testnet_hived_image` job on `develop`.
2. Resolve it to a digest:
   `docker buildx imagetools inspect registry.gitlab.syncad.com/hive/hive/testnet:<tag>`.
   Untagged commit images are garbage-collected from hive's registry (the `7abd5aba` image
   clive's last green develop pipeline used is already gone), which is one more reason to pin
   a release or `hived-for-clive-*` tag when there is one.
3. Put the digest into the `COPY --from=` line of the Dockerfile and update the pin above.
4. Rebuild and re-pin as below.

### Rebuilding the image

Rebuild with `.aidev/runtime/build.sh --push` when the Dockerfile, `pyproject.toml`,
`poetry.lock` or `tests/clive-local-tools/{pyproject.toml,poetry.lock}` changes, and put the
printed `repo@sha256:…` into `environment.image`. `AIDEV_RUNTIME_BUILDER` selects a buildx
builder (one that mirrors `registry.gitlab.syncad.com` makes the hive images quick to pull).
