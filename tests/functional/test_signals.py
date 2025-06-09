from __future__ import annotations

import asyncio
import os
import signal
import subprocess
from copy import deepcopy
from typing import Final

import pytest
import test_tools as tt

from clive.__private.core.commands.beekeeper import IsBeekeeperRunning
from clive.__private.core.constants.setting_identifiers import DATA_PATH
from clive.__private.settings import clive_prefixed_envvar, safe_settings
from clive_local_tools.waiters import wait_for


@pytest.mark.parametrize("signal_number", [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM])
async def test_close_on_signal(signal_number: signal.Signals) -> None:
    # ARRANGE
    def get_process_return_code() -> int | None:
        return process.returncode

    async def should_beekeeper_be_running(*, expected: bool) -> bool:
        result = await IsBeekeeperRunning().execute_with_result()
        return result.is_running == expected

    working_directory = tt.context.get_current_directory()
    entry_point: Final[str] = "clive"
    envs = deepcopy(os.environ)
    envs[clive_prefixed_envvar(DATA_PATH)] = working_directory.as_posix()
    clive_output = working_directory / "clive_output.log"
    clive_startup_screen_text: Final[str] = "Let's create profile!"

    # ACT
    with clive_output.open("w") as out:
        process = await asyncio.create_subprocess_exec(
            entry_point, stdout=out, stderr=out, stdin=subprocess.PIPE, env=envs
        )

        await wait_for(
            lambda: should_beekeeper_be_running(expected=True),
            "Beekeeper did not spawn",
            timeout=safe_settings.beekeeper.initialization_timeout,
        )

        tt.logger.info("Waiting for clive to start up...")
        await wait_for(lambda: clive_startup_screen_text in clive_output.read_text(), "Clive did not start")

        tt.logger.info(f"Sending signal: {signal_number}")
        process.send_signal(signal_number)

        # ASSERT
        await wait_for(
            lambda: get_process_return_code() == 0,
            lambda: f"Clive tui process not closed properly. Return code is {get_process_return_code()}",
        )
        await wait_for(lambda: should_beekeeper_be_running(expected=False), "Beekeeper did not close")
