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
from clive.__private.core.constants.setting_identifiers import BEEKEEPER_SESSION_TOKEN
from clive.__private.settings import clive_prefixed_envvar


@dataclass(kw_only=True)
class BeekeeperInfo(BeekeeperBasedCommand):
    async def _run(self) -> None:
        typer.echo((await self.beekeeper.api.get_info()).json(by_alias=True))


@dataclass(kw_only=True)
class BeekeeperCreateSession(BeekeeperBasedCommand):
    echo_token_only: bool

    async def _run(self) -> None:
        token = await self.beekeeper.create_session_token()
        if self.echo_token_only:
            message = token
        else:
            message = (
                f"A new session was created, token is: {token}\n"
                "If you want to use that Beekeeper session in Clive CLI env, please set:\n"
                f"export {clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)}={token}"
            )
        typer.echo(message=message)

    async def _hook_before_entering_context_manager(self) -> None:
        """Display information about using Beekeeper if not using echo-token-only flag."""
        if not self.echo_token_only:
            await super()._hook_before_entering_context_manager()


@dataclass(kw_only=True)
class BeekeeperSpawn(ExternalCLICommand):
    background: bool

    async def validate(self) -> None:
        await self._validate_beekeeper_is_not_running()
        await super().validate()

    async def _run(self) -> None:
        typer.echo("Launching beekeeper...")

        async with Beekeeper(run_in_background=self.background) as beekeeper:
            typer.echo(f"Beekeeper started on {beekeeper.http_endpoint} with pid {beekeeper.pid}.")

            if not self.background:
                self.__serve_forever()

    async def _validate_beekeeper_is_not_running(self) -> None:
        if await Beekeeper.is_already_running_locally():
            message = (
                f"Beekeeper is already running on {Beekeeper.get_remote_address_from_connection_file()} with pid"
                f" {Beekeeper.get_pid_from_file()}"
            )
            raise CLIPrettyError(message, errno.EEXIST)

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
