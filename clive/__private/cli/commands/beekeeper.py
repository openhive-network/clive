import errno
import math
import os
import signal
import time
from dataclasses import dataclass
from pathlib import Path

import typer

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli_error import CLIError
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.commands.activate import ActivateInvalidPasswordError, WalletDoesNotExistsError
from clive.__private.core.keys import (
    KeyAliasAlreadyInUseError,
    PrivateKey,
    PrivateKeyAliased,
    PrivateKeyInvalidFormatError,
)


@dataclass(kw_only=True)
class BeekeeperInfo(BeekeeperBasedCommand):
    async def run(self) -> None:
        typer.echo((await self.beekeeper.api.get_info()).json(by_alias=True))


@dataclass(kw_only=True)
class BeekeeperSpawn(ExternalCLICommand):
    background: bool

    async def run(self) -> None:
        if Beekeeper.is_already_running_locally():
            message = (
                f"Beekeeper is already running on {Beekeeper.get_remote_address_from_connection_file()} with pid"
                f" {Beekeeper.get_pid_from_file()}"
            )
            raise CLIError(message, errno.EEXIST)

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
    async def run(self) -> None:
        pid = Beekeeper.get_pid_from_file()
        typer.echo(f"Closing beekeeper with pid {pid}...")

        sig = signal.SIGINT
        os.kill(pid, sig)

        try:
            self.__wait_for_pid_to_die(pid, timeout_secs=10)
        except TimeoutError:
            sig = signal.SIGKILL
            os.kill(pid, sig)
            self.__wait_for_pid_to_die(pid)

        signal_name = signal.Signals(sig).name
        typer.echo(f"Beekeeper was closed with {signal_name}.")

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


@dataclass(kw_only=True)
class BeekeeperImportKey(WorldBasedCommand):
    password: str
    key_or_path: str | Path
    """str might be a path to a file or a private key value."""

    alias: str | None = None

    @property
    def private_key_aliased(self) -> PrivateKeyAliased:
        key_or_path = Path(self.key_or_path)

        if key_or_path.is_file():
            private_key = PrivateKey.from_file(key_or_path)
        else:
            try:
                private_key = PrivateKey(value=str(self.key_or_path))
            except PrivateKeyInvalidFormatError as error:
                raise CLIError(str(error), errno.EINVAL) from None

        alias = self.alias if self.alias else private_key.calculate_public_key().value

        return private_key.with_alias(alias)

    async def run(self) -> None:
        profile_data = self.world.profile_data
        if not profile_data.is_working_account_set():
            raise CLIError("Working account is not set", errno.ENOENT)

        typer.echo("Importing key...")

        try:
            profile_data.working_account.keys.add_to_import(self.private_key_aliased)
        except KeyAliasAlreadyInUseError as error:
            raise CLIError(str(error), errno.EEXIST) from None

        try:
            await self.world.commands.activate(password=self.password)
        except ActivateInvalidPasswordError:
            raise CLIError("Invalid password.") from None
        except WalletDoesNotExistsError:
            raise CLIError("Wallet does not exists.") from None

        await self.world.commands.sync_data_with_beekeeper()

        typer.echo("Key imported.")
