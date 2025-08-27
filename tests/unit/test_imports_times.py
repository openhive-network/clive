from __future__ import annotations

from clive_local_tools.cli.imports import get_autocompletion_time, get_cli_help_imports_time


def test_autocompletion_time() -> None:
    # ARRANGE
    seconds_threshold = 0.5

    # ACT
    import_time = get_autocompletion_time()

    # ASSERT
    message = (
        f"Autocompletion time `{import_time}s` exceeds `{seconds_threshold}s`\n"
        "Please check for any unnecessary imports in autocompletion mode."
    )
    assert import_time < seconds_threshold, message


def test_clive_help_imports_time() -> None:
    # ARRANGE
    seconds_threshold = 0.5

    # ACT
    import_time = get_cli_help_imports_time()

    # ASSERT
    message = (
        f"`clive --help` import time `{import_time}s` exceeds `{seconds_threshold}s`\n"
        "Please check for any unnecessary imports."
    )
    assert import_time < seconds_threshold, message
