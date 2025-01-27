from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command import Command, CommandError
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.settings import safe_settings

if TYPE_CHECKING:
    from pathlib import Path


class BeekeeperPIDFileNotFoundError(CommandError):
    def __init__(self, command: Command) -> None:
        super().__init__(command, "Beekeeper PID file was not found. Is it running?")


@dataclass(kw_only=True)
class BeekeeperLoadDetachedPID(CommandWithResult[int]):
    async def _execute(self) -> None:
        beekeeper_pid_file_path = self._get_beekeeper_pid_file_path()
        if not beekeeper_pid_file_path.exists():
            raise BeekeeperPIDFileNotFoundError(self)

        data = json.loads(beekeeper_pid_file_path.read_text())
        assert "pid" in data, "Beekeeper PID file is corrupted"
        self._result = int(data["pid"])

    @staticmethod
    def _get_beekeeper_pid_file_path() -> Path:
        return safe_settings.data_path / "beekeeper/beekeeper.pid"


@dataclass
class IsBeekeeperRunningResult:
    is_running: bool
    pid: int | None

    @property
    def pid_ensure(self) -> int:
        assert self.pid is not None, "pid is not set."
        return self.pid


@dataclass(kw_only=True)
class IsBeekeeperRunning(CommandWithResult[IsBeekeeperRunningResult]):
    async def _execute(self) -> None:
        try:
            beekeeper_pid = await BeekeeperLoadDetachedPID().execute_with_result()
        except BeekeeperPIDFileNotFoundError:
            self._result = IsBeekeeperRunningResult(is_running=False, pid=None)
        else:
            is_beekeeper_running = self._is_pid_exists(beekeeper_pid)
            self._result = IsBeekeeperRunningResult(is_running=is_beekeeper_running, pid=beekeeper_pid)

    @staticmethod
    def _is_pid_exists(pid: int) -> bool:
        """
        Check for the existence of a unix pid.

        credit: https://stackoverflow.com/a/20186516
        """
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False  # No such process
        except PermissionError:
            return True  # Operation not permitted (i.e., process exists)
        else:
            return True  # No error, we can send a signal to the process
