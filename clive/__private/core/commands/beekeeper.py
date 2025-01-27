from __future__ import annotations

import errno
import json
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import typer
from helpy import HttpUrl

from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.settings import safe_settings

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(kw_only=True)
class BeekeeperProcessInfo:
    pid: int | None = None
    endpoint: HttpUrl | None = None

    def __str__(self) -> str:
        endpoint = self.endpoint.as_string() if self.endpoint is not None else None
        return f"{self.__class__.__name__}(pid={self.pid}, {endpoint=})"

    def is_set(self) -> bool:
        return self.pid is not None and self.endpoint is not None


@dataclass(kw_only=True)
class BeekeeperPidFileAccessor:
    working_directory: Path = field(default_factory=lambda: safe_settings.data_path)

    @property
    def _beekeeper_process_info_file(self) -> Path:
        return self.working_directory / "clive_beekeeper.pid"


@dataclass(kw_only=True)
class BeekeeperSaveDetached(BeekeeperPidFileAccessor, Command):
    pid: int
    endpoint: str

    async def _execute(self) -> None:
        if self._beekeeper_process_info_file.exists():
            typer.echo(f"`{self._beekeeper_process_info_file}` exists; does other beekeeper is still running?")
            self._beekeeper_process_info_file.unlink()
        self._beekeeper_process_info_file.write_text(json.dumps([self.pid, self.endpoint]))
        typer.echo(
            f"Saved pid = {self.pid} and endpoint = {self.endpoint} in `{self._beekeeper_process_info_file.as_posix()}`"
        )


@dataclass(kw_only=True)
class BeekeeperLoadDetachedPID(BeekeeperPidFileAccessor, CommandWithResult[BeekeeperProcessInfo]):
    remove_file: bool = True
    silent_fail: bool = False

    async def _execute(self) -> None:
        if not self._beekeeper_process_info_file.exists():
            if not self.silent_fail:
                raise CLIPrettyError(f"`{self._beekeeper_process_info_file}` does not exists", errno.EEXIST)
            self._result = BeekeeperProcessInfo()
            return
        loaded = json.loads(self._beekeeper_process_info_file.read_text().strip())
        self._result = BeekeeperProcessInfo(pid=loaded[0], endpoint=HttpUrl(loaded[1]))
        typer.echo(f"Loaded pid = {self._result} from `{self._beekeeper_process_info_file.as_posix()}`")
        if self.remove_file:
            self._beekeeper_process_info_file.unlink()


@dataclass(kw_only=True)
class IsBeekeeperRunning(BeekeeperPidFileAccessor, CommandWithResult[bool]):
    beekeeper_process_info: BeekeeperProcessInfo | None = field(init=False)
    """This is extra result and is optimization to reuse gathered information"""

    async def _execute(self) -> None:
        if not self._beekeeper_process_info_file.exists():
            self._result = False
            return

        self.beekeeper_process_info = await BeekeeperLoadDetachedPID(remove_file=False).execute_with_result()

        self._result = (
            self.beekeeper_process_info.is_set()
            and self.beekeeper_process_info.pid is not None
            and self.is_pid_exists(self.beekeeper_process_info.pid)
        )

    def is_pid_exists(self, pid: int) -> bool:
        """
        Check For the existence of a unix pid.

        credit: https://stackoverflow.com/a/568285
        """
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            # credit: https://stackoverflow.com/questions/568271/how-to-check-if-there-exists-a-process-with-a-given-pid-in-python#comment83920380_41851786
            return False
        else:
            return True
