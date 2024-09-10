from __future__ import annotations

import asyncio
import os
import signal
import subprocess
from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.constants.setting_identifiers import DATA_PATH
from clive.__private.settings import clive_prefixed_envvar

if TYPE_CHECKING:
    from collections.abc import Callable


async def wait_for(condition: Callable[[], bool], message: str, timeout: float = 10.0) -> None:
    async def __wait_for() -> None:
        while not condition():
            await asyncio.sleep(0.1)

    try:
        await asyncio.wait_for(__wait_for(), timeout=timeout)
    except asyncio.TimeoutError:
        raise AssertionError(f"{message}, wait_for timeout is {timeout:.2f}") from None


@pytest.mark.parametrize("signal_number", [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM])
async def test_close_on_signal(signal_number: signal.Signals) -> None:
    # ARRANGE
    working_directory = tt.context.get_current_directory()
    entry_point: Final[str] = "clive"
    envs = os.environ
    envs[clive_prefixed_envvar(DATA_PATH)] = working_directory.as_posix()
    beekeeper_pidfile = working_directory / "beekeeper" / "beekeeper.pid"
    clive_output = working_directory / "clive_output.log"

    # ACT
    with clive_output.open("w") as out:
        process = await asyncio.create_subprocess_exec(
            entry_point, stdout=out, stderr=out, stdin=subprocess.PIPE, env=envs
        )
        await wait_for(lambda: beekeeper_pidfile.exists(), "Beekeeper did not spawn")
        await wait_for(lambda: process.returncode is None, "Clive tui process is not running")
        process.send_signal(signal_number)

        # ASSERT
        await wait_for(lambda: not beekeeper_pidfile.exists(), "Beekeeper did not close")
        await wait_for(lambda: process.returncode == 0, "Clive tui process is still running")
