import errno
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import typer
from beekeepy import AsyncBeekeeper, close_already_running_beekeeper
from beekeepy.exceptions import BeekeeperFailedToStartError
from helpy import HttpUrl

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.settings import safe_settings


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
class BeekeeperInfo(BeekeeperBasedCommand):
    async def _run(self) -> None:
        info = await (await self.beekeeper.session).get_info()
        typer.echo(info.json())


@dataclass(kw_only=True)
class BeekeeperPidFileAccessor:
    working_directory: Path = field(
        default_factory=lambda: safe_settings.beekeeper.settings_factory().working_directory
    )

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
class BeekeeperSpawn(ExternalCLICommand):
    background: bool

    async def _run(self) -> None:
        try:
            async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_factory()) as beekeeper:
                typer.echo("Beekeeper started")

                if not self.background:
                    self.__serve_forever()
                else:
                    pid = beekeeper.detach()
                    endpoint = beekeeper.pack().settings.http_endpoint
                    assert endpoint is not None, "Endpoint from packed settings is None"
                    await BeekeeperSaveDetached(pid=pid, endpoint=endpoint.as_string()).execute()
                    typer.echo(f"Beekeeper is now running in background with {pid=}")
        except BeekeeperFailedToStartError as e:
            message = "Failed to start beekeeper. Is beekeeper already running?"
            raise CLIPrettyError(message, errno.EEXIST) from e

    @staticmethod
    def __serve_forever() -> None:
        typer.echo("Press Ctrl+C to exit.")

        while True:
            time.sleep(1)


@dataclass(kw_only=True)
class BeekeeperClose(ExternalCLICommand):
    async def _run(self) -> None:
        pid = (await BeekeeperLoadDetachedPID().execute_with_result()).pid
        assert pid is not None, "Cannot automatically determine beekeeper PID, missing file"
        close_already_running_beekeeper(pid=pid)
