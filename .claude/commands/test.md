Run pytest with the provided arguments.

Arguments: $ARGUMENTS

First, expand any shortcuts in the arguments:

-   `unit` → `tests/unit/`
-   `cli` → `tests/functional/cli/`
-   `tui` → `tests/functional/tui/`
-   `functional` → `tests/functional/`

Then execute pytest with the expanded path. Examples:

-   `/test unit` runs `pytest tests/unit/`
-   `/test cli` runs `pytest tests/functional/cli/`
-   `/test tests/unit/test_date_utils.py -v` runs as-is (full path provided)

If no arguments provided, run all tests with parallel execution:

```bash
pytest -n 16
```

Report results concisely:

-   Number of tests passed/failed/skipped
-   For failures, show the test name and a brief summary of the error
-   Suggest next steps if tests fail
