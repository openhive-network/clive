from __future__ import annotations

import subprocess
from time import perf_counter


def test_clive_help_command_execution_time() -> None:
    # ARRANGE
    seconds_threshold = 0.5
    command = "clive --help"

    # ACT
    start_time = perf_counter()
    subprocess.run(command, shell=True, check=True)
    end_time = perf_counter()
    actual_execution_time = end_time - start_time

    # ASSERT
    message = (
        f"Command '{command}' execution time {actual_execution_time:.2f}s exceeds `{seconds_threshold}s`\n"
        "Check for performance issues or unnecessary imports that might be slowing down command execution."
    )
    assert actual_execution_time < seconds_threshold, message
