#!/usr/bin/env bash
# The checks AIDEV's verification slots run (.aidev/project.yaml), as one junit
# report per suite: each named step is a test case, its log the failure body, and
# every pytest step also keeps pytest's own junit (one case per test) next to it.
#
#   .aidev/run-checks.sh <suite> <step>...
#
#   static          ruff check, ruff format --check, mypy on clive/ tests/ (CI's
#                   lint_code_with_ruff, formatting_with_ruff_check, type_check_with_mypy)
#                   and the private-key/password logging scan; one case each
#   ruff | ruff-format | mypy | secrets   the same, one at a time
#   unit            pytest -n 16 tests/unit without the load-sensitive timing tests
#                   (CI runs those alone, in testing_clive_times)
#   functional-cli  pytest -n 16 tests/functional/cli (CI's testing_cli)
#   functional      CI's testing_clive selection: everything but tests/functional/tui,
#                   tests/functional/cli, the timing tests and tests/unit/async_hived
#                   (CI's test_async_hived)
#   tui             pytest -n 16 tests/functional/tui (CI's testing_tui)
#   coverage        `unit` with --cov=clive (coverage.xml in test-results/<suite>/)
#
# Node-based tests start a TESTNET hived through test-tools (HIVED_PATH & co. and the
# mainnet beekeeper are baked into the image of .aidev/runtime/Dockerfile); suites
# run offline in that image.
# The step functions below are only called through step(), which shellcheck can't see.
# shellcheck disable=SC2317
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
root="$PWD"
suite="${1:?usage: $0 <suite> <step>...}"; shift
out="$root/test-results/$suite"
rm -rf "$out"; mkdir -p "$out"
cases="$out/cases.tsv"; : > "$cases"
# shellcheck source=.aidev/junit-helpers.sh disable=SC1091
source .aidev/junit-helpers.sh

# CI's .testing variables: generous timeouts, as on a loaded shared runner.
export CLIVE_BEEKEEPER__COMMUNICATION_TOTAL_TIMEOUT_SECS=60 \
       CLIVE_NODE__COMMUNICATION_TOTAL_TIMEOUT_SECS=60 \
       CLIVE_BEEKEEPER__INITIALIZATION_TIMEOUT=60 \
       CLIVE_BEEKEEPER__CLOSE_TIMEOUT=60 \
       BEEKEEPY_INITIALIZATION_TIMEOUT=60 \
       BEEKEEPY_CLOSE_TIMEOUT=60 \
       TEST_TOOLS_NODE_DEFAULT_WAIT_FOR_LIVE_TIMEOUT=60
export HOME="${HOME:-/tmp}"

status=0
step() {
    local name="$1"; shift
    local log="$out/$name.log" t0=$SECONDS rc=0
    echo "== $name" >&2
    ( cd "$root" && "$@" ) > "$log" 2>&1 < /dev/null || rc=$?   # a step's cd stays in its subshell
    if [ "$rc" -eq 0 ]; then
        printf 'case\t%s\tpass\t%s\t\n' "$name" "$((SECONDS - t0))" >> "$cases"
    else
        status=1; tail -40 "$log" >&2
        printf 'case\t%s\tfail\t%s\texit %s\t%s\n' "$name" "$((SECONDS - t0))" "$rc" "$log" >> "$cases"
    fi
}

packages=(clive/ tests/)   # CI's PACKAGES_TO_CHECK
timing_tests=(tests/unit/test_imports_times.py tests/unit/test_command_execution_times.py)

# As CI's .run-pytest: --timeout (PYTEST_TIMEOUT_MINUTES 10), -n 16, --durations=0.
run_pytest() {
    local name="$1"; shift
    local junit="$out/$name-junit.xml"
    rm -f "$junit"
    run_with_junit_fallback "$junit" "$name" \
        python3 -m pytest -p no:cacheprovider --timeout=600 -n 16 --durations=0 --junitxml="$junit" "$@"
}

secrets_scan() {
    # CI's testing_password_private_key_logging: scans the clive logs the test runs
    # left under tests/ (nothing to scan when no test step ran in this checkout).
    cd tests && bash "$root/scripts/check_for_private_key_or_password_logging.bash"
}

for s in "$@"; do
    case "$s" in
        static)
            step ruff ruff check "${packages[@]}"
            step ruff-format ruff format --check --diff "${packages[@]}"
            step mypy mypy "${packages[@]}"
            step secrets secrets_scan ;;
        ruff) step ruff ruff check "${packages[@]}" ;;
        ruff-format) step ruff-format ruff format --check --diff "${packages[@]}" ;;
        mypy) step mypy mypy "${packages[@]}" ;;
        secrets) step secrets secrets_scan ;;
        unit) step unit run_pytest unit "${timing_tests[@]/#/--ignore=}" tests/unit ;;
        functional-cli) step functional-cli run_pytest functional-cli tests/functional/cli ;;
        functional)
            step functional run_pytest functional \
                --ignore=tests/functional/tui --ignore=tests/functional/cli \
                "${timing_tests[@]/#/--ignore=}" --ignore=tests/unit/async_hived tests ;;
        tui) step tui run_pytest tui tests/functional/tui ;;
        coverage)
            step coverage run_pytest coverage --cov=clive --cov-report=xml:"$out/coverage.xml" \
                --cov-report=term "${timing_tests[@]/#/--ignore=}" tests/unit ;;
        *) printf 'case\t%s\tfail\t0\tunknown step\n' "$s" >> "$cases"; status=1 ;;
    esac
done
junit_write_cases "$out/junit.xml" "$suite" "$cases"
exit "$status"
