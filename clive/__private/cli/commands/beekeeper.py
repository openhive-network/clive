import time
from dataclasses import dataclass

import typer
from beekeepy import AsyncBeekeeper, close_already_running_beekeeper

from clive.__private.cli.commands.abc.beekeeper_based_command import BeekeeperBasedCommand
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import (
    CLIBeekeeperCannotSpawnNewInstanceWithEnvSetError,
    CLIBeekeeperLocallyAlreadyRunningError,
)
from clive.__private.core.commands.beekeeper import BeekeeperLoadDetachedPID, IsBeekeeperRunning
from clive.__private.core.constants.setting_identifiers import BEEKEEPER_REMOTE_ADDRESS, BEEKEEPER_SESSION_TOKEN
from clive.__private.settings import clive_prefixed_envvar, safe_settings


@dataclass(kw_only=True)
class BeekeeperInfo(BeekeeperBasedCommand):
    async def _run(self) -> None:
        session = await self.beekeeper.session
        info = (await session.get_info()).json()
        typer.echo(info)


@dataclass(kw_only=True)
class BeekeeperCreateSession(BeekeeperBasedCommand):
    echo_token_only: bool

    async def _run(self) -> None:
        session = await self.beekeeper.create_session()
        token = await session.token
        if self.echo_token_only:
            message = token
        else:
            message = (
                f"A new session was created, token is: {token}\n"
                "If you want to use that Beekeeper session in Clive CLI env, please set:\n"
                f"export {clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)}={token}"
            )
        typer.echo(message=message)

    @property
    def _is_session_token_required(self) -> bool:
        return False

    async def _hook_before_entering_context_manager(self) -> None:
        """Display information about using Beekeeper if not using echo-token-only flag."""
        if not self.echo_token_only:
            await super()._hook_before_entering_context_manager()


@dataclass(kw_only=True)
class BeekeeperSpawn(ExternalCLICommand):
    background: bool
    echo_address_only: bool

    async def validate(self) -> None:
        await self._validate_beekeepers_env_vars_not_set()
        await self._validate_beekeeper_is_not_running()
        await super().validate()

    async def _run(self) -> None:
        if not self.echo_address_only:
            typer.echo("Launching beekeeper...")

        async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_local_factory()) as beekeeper:
            pid = beekeeper.detach()

            if self.echo_address_only:
                message = str(beekeeper.http_endpoint)
            else:
                session = await beekeeper.session
                token = await session.token
                message = (
                    f"Beekeeper started on {beekeeper.http_endpoint} with pid {pid}.\n"
                    "If you want to use that beekeeper in Clive CLI env, please set:\n"
                    f"export {clive_prefixed_envvar(BEEKEEPER_REMOTE_ADDRESS)}={beekeeper.http_endpoint}\n"
                    f"export {clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)}={token}"
                )
            typer.echo(message=message)

            if not self.background:
                self.__serve_forever()

    async def _validate_beekeepers_env_vars_not_set(self) -> None:
        """
        Do not spawn new instance of Beekeeper.

        In order to avoid miss-configrutaion with using Beekeeper we should avoid spawning
        new instance(s) of Beekeeper while CLIVE_BEEKEEPEER__SESSION_TOKEN and
        CLIVE_BEEKEEPER__REMOTE_ADDRES are set.
        """
        if safe_settings.beekeeper.is_remote_address_set or safe_settings.beekeeper.is_session_token_set:
            raise CLIBeekeeperCannotSpawnNewInstanceWithEnvSetError

    async def _validate_beekeeper_is_not_running(self) -> None:
        result = await IsBeekeeperRunning().execute_with_result()
        if result.is_running:
            raise CLIBeekeeperLocallyAlreadyRunningError(result.pid_ensure)

    @staticmethod
    def __serve_forever() -> None:
        typer.echo("Press Ctrl+C to exit.")

        while True:
            time.sleep(1)


@dataclass(kw_only=True)
class BeekeeperClose(ExternalCLICommand):
    async def _run(self) -> None:
        pid = await BeekeeperLoadDetachedPID().execute_with_result()
        typer.echo(f"Closing beekeeper with pid {pid}...")
        close_already_running_beekeeper(pid=pid)
        typer.echo("Beekeeper was closed with.")
