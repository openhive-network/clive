from __future__ import annotations

from clive_local_tools.cli.timing import get_cli_help_execution_time


def test_clive_help_command_execution_time() -> None:
    # ARRANGE
    seconds_threshold = 0.5

    # ACT
    actual_execution_time = get_cli_help_execution_time()

    # ASSERT
    message = (
        f"Command 'clive --help' execution time {actual_execution_time:.2f}s exceeds `{seconds_threshold}s`\n"
        "Check for performance issues or unnecessary imports that might be slowing down command execution."
    )
    assert actual_execution_time < seconds_threshold, message
