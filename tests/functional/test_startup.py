from __future__ import annotations

import os
import signal
import subprocess
import time
from copy import deepcopy
from typing import Final

import test_tools as tt

from clive.__private.core.constants.setting_identifiers import DATA_PATH
from clive.__private.settings import clive_prefixed_envvar


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
    working_directory = tt.context.get_current_directory()
    entry_point: Final[str] = "clive-dev"
    envs = deepcopy(os.environ)
    envs[clive_prefixed_envvar(DATA_PATH)] = working_directory.as_posix()
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
