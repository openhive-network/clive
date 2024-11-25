import errno
import time
from dataclasses import dataclass
from pathlib import Path

import typer
from beekeepy import AsyncBeekeeper, close_already_running_beekeeper
from beekeepy.exceptions import BeekeeperFailedToStartError

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from clive.__private.settings import safe_settings


@dataclass(kw_only=True)
class BeekeeperInfo(BeekeeperBasedCommand):
    async def _run(self) -> None:
        info = await (await self.beekeeper.session).get_info()
        typer.echo(info.json())


class BeekeeperPidFileAccessor:
    @property
    def _pid_file(self) -> Path:
        return safe_settings.beekeeper.settings_factory().working_directory / "clive_beekeeper.pid"


@dataclass(kw_only=True)
class BeekeeperSaveDetachedPID(BeekeeperPidFileAccessor, Command):
    pid: int

    async def _execute(self) -> None:
        if self._pid_file.exists():
            typer.echo(f"`{self._pid_file}` exists; does other beekeeper is still running?")
            self._pid_file.unlink()
        self._pid_file.write_text(str(self.pid))
        typer.echo(f"Saved pid = {self.pid} in `{self._pid_file.as_posix()}`")


@dataclass(kw_only=True)
class BeekeeperLoadDetachedPID(BeekeeperPidFileAccessor, CommandWithResult[int]):
    async def _execute(self) -> None:
        if not self._pid_file.exists():
            raise CLIPrettyError(f"`{self._pid_file}` does not exists", errno.EEXIST)
        self._result = int(self._pid_file.read_text().strip())
        typer.echo(f"Loaded pid = {self._result} from `{self._pid_file.as_posix()}`")
        self._pid_file.unlink()


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
                    await BeekeeperSaveDetachedPID(pid=pid).execute()
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
        close_already_running_beekeeper(pid=(await BeekeeperLoadDetachedPID().execute_with_result()))
