from __future__ import annotations

import os
import signal
import subprocess
import time
from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from pathlib import Path


def test_if_entry_point_works() -> None:
    # ARRANGE
    entry_point: Final[str] = "clive --help"
    exit_code_successful: Final[int] = 0

    # ACT
    status, result = subprocess.getstatusoutput(entry_point)

    # ASSERT
    assert status == exit_code_successful, f"`{entry_point}` command failed because of: `{result}`"


@pytest.mark.random_fail
def test_if_dev_entry_point_works(working_directory: Path) -> None:
    # ARRANGE
    entry_point: Final[str] = "clive-dev"
    envs = os.environ
    envs["CLIVE_DATA_PATH"] = working_directory.as_posix()
    beekeeper_pid = working_directory / "beekeeper" / "beekeeper.pid"
    beekeeper_output = working_directory / "test_output.log"

    # ACT
    with beekeeper_output.open("w") as out:
        process = subprocess.Popen([entry_point], stdout=out, stderr=out, env=envs)

        # Give the process some time to start
        time.sleep(1)

        # ASSERT
        running = not process.poll()
        assert running
        process.terminate()

    # clean up
    if beekeeper_pid.exists():
        with beekeeper_pid.open("r") as file:
            os.kill(int(file.readline().strip()), signal.SIGINT)
