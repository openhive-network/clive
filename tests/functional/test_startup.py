from __future__ import annotations

import subprocess
import time
from typing import Final


def test_if_entry_point_works() -> None:
    # ARRANGE
    entry_point: Final[str] = "clive --help"
    exit_code_successful: Final[int] = 0

    # ACT
    status, result = subprocess.getstatusoutput(entry_point)

    # ASSERT
    assert status == exit_code_successful, f"`{entry_point}` command failed because of: `{result}`"


def test_if_dev_entry_point_works() -> None:
    # ARRANGE
    entry_point: Final[str] = "clive-dev"

    # ACT
    process = subprocess.Popen([entry_point], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Give the process some time to start
    time.sleep(1)

    # ASSERT
    running = not process.poll()
    assert running, f"App failed to start.  Stderr: {process.stderr.read().decode() if process.stderr else 'N/A'}"

    process.terminate()  # If it is running, terminate it - that means app was launched successfully
