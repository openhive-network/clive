from __future__ import annotations

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
from clive.__private.core.commands.beekeeper import BeekeeperLoadDetachedPID, BeekeeperSaveDetached, IsBeekeeperRunning
from clive.__private.core.constants.setting_identifiers import BEEKEEPER_REMOTE_ADDRESS, BEEKEEPER_SESSION_TOKEN
from clive.__private.settings import safe_settings
from clive.__private.settings._settings import clive_prefixed_envvar


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

        async with await AsyncBeekeeper.factory(settings=safe_settings.beekeeper.settings_factory()) as beekeeper:
            beekeeper_settings = beekeeper.pack().settings
            beekeeper_endpoint = beekeeper_settings.http_endpoint
            assert beekeeper_endpoint is not None, "started beekeeper has no address, critical error!"
            pid = beekeeper.detach()
            await BeekeeperSaveDetached(pid=pid, endpoint=beekeeper_endpoint.as_string()).execute()

            if self.echo_address_only:
                message = beekeeper_endpoint.as_string()
            else:
                message = (
                    f"Beekeeper started on {beekeeper_endpoint.as_string()} with {pid=}.\n"
                    "If you want to use that beekeeper in Clive CLI env, please set:\n"
                    f"export {clive_prefixed_envvar(BEEKEEPER_REMOTE_ADDRESS)}={beekeeper_endpoint.as_string()}\n"
                    f"export {clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)}={await (await beekeeper.session).token}"
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
        command = IsBeekeeperRunning()
        if await command.execute_with_result():
            # assertions because of mypy
            assert command.beekeeper_process_info is not None, "beekeeper_process_info is None"
            assert command.beekeeper_process_info.endpoint is not None, "beekeeper_process_info.endpoint is None"
            assert command.beekeeper_process_info.pid is not None, "beekeeper_process_info.pid is None"

            raise CLIBeekeeperLocallyAlreadyRunningError(
                url=command.beekeeper_process_info.endpoint, pid=command.beekeeper_process_info.pid
            )

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


@dataclass(kw_only=True)
class BeekeeperCreateSession(BeekeeperBasedCommand):
    echo_token_only: bool

    async def _run(self) -> None:
        session = await self.beekeeper.create_session()
        if self.echo_token_only:
            message = await session.token
        else:
            message = (
                f"A new session was created, token is: {await session.token}\n"
                "If you want to use that Beekeeper session in Clive CLI env, please set:\n"
                f"export {clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)}={await session.token}"
            )
        typer.echo(message=message)


@dataclass(kw_only=True)
class BeekeeperInfo(BeekeeperBasedCommand):
    async def _run(self) -> None:
        typer.echo((await (await self.beekeeper.session).get_info()).json())
