import errno
import math
import os
import signal
import time
from dataclasses import dataclass

import typer

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.beekeeper.config import BeekeeperConfig


@dataclass(kw_only=True)
class BeekeeperInfo(BeekeeperBasedCommand):
    async def _run(self) -> None:
        typer.echo((await self.beekeeper.api.get_info()).json(by_alias=True))


@dataclass(kw_only=True)
class BeekeeperSpawn(ExternalCLICommand):
    background: bool

    async def _run(self) -> None:
        if Beekeeper.is_already_running_locally():
            message = (
                f"Beekeeper is already running on {Beekeeper.get_remote_address_from_connection_file()} with pid"
                f" {Beekeeper.get_pid_from_file()}"
            )
            raise CLIPrettyError(message, errno.EEXIST)

        typer.echo("Launching beekeeper...")

        async with Beekeeper(run_in_background=self.background) as beekeeper:
            typer.echo(f"Beekeeper started on {beekeeper.http_endpoint} with pid {beekeeper.pid}.")

            if not self.background:
                self.__serve_forever()

    @staticmethod
    def __serve_forever() -> None:
        typer.echo("Press Ctrl+C to exit.")

        while True:
            time.sleep(1)


@dataclass(kw_only=True)
class BeekeeperClose(ExternalCLICommand):
    async def _run(self) -> None:
        pid = Beekeeper.get_pid_from_file()
        typer.echo(f"Closing beekeeper with pid {pid}...")

        try:
            sig = signal.SIGINT
            os.kill(pid, sig)
        except ProcessLookupError:
            # If this exception occurs, it means that something wrong happens to beekeeper.
            # So, we need to remove trash.
            self._remove_dangling_files()
            raise

        try:
            self.__wait_for_pid_to_die(pid, timeout_secs=10)
        except TimeoutError:
            sig = signal.SIGKILL
            os.kill(pid, sig)
            self.__wait_for_pid_to_die(pid)

        signal_name = signal.Signals(sig).name
        typer.echo(f"Beekeeper was closed with {signal_name}.")

    def _remove_dangling_files(self) -> None:
        import pathlib

        beekeeper_path = BeekeeperConfig.get_wallet_dir()
        if beekeeper_path:
            connection_file = beekeeper_path / "beekeeper.connection"
            pid_file = beekeeper_path / "beekeeper.pid"
            wallet_lock_file = beekeeper_path / "beekeeper.wallet.lock"
            if connection_file.is_file():
                pathlib.Path.unlink(connection_file)
            if pid_file.is_file():
                pathlib.Path.unlink(pid_file)
            if wallet_lock_file.is_file():
                pathlib.Path.unlink(wallet_lock_file)

    @classmethod
    def __wait_for_pid_to_die(cls, pid: int, *, timeout_secs: float = math.inf) -> None:
        sleep_time = min(1.0, timeout_secs)
        already_waited = 0.0
        while not cls.__is_running(pid):
            if timeout_secs - already_waited <= 0:
                raise TimeoutError(f"Process with pid {pid} didn't die in {timeout_secs} seconds.")

            time.sleep(sleep_time)
            already_waited += sleep_time

    @staticmethod
    def __is_running(pid: int) -> bool:
        """
        Check whether pid exists in the current process table.

        Source: https://stackoverflow.com/a/7654102

        Args:
        ----
        pid: The Process ID to check.

        Returns:
        -------
        True if process with the given pid is running else False.
        """
        try:
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                return False
        return True
