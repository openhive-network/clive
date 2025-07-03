from __future__ import annotations

import time
from dataclasses import dataclass

import typer
from beekeepy import AsyncBeekeeper, close_already_running_beekeeper
from beekeepy.exceptions import FailedToDetectRunningBeekeeperError

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.exceptions import (
    CLIBeekeeperCannotSpawnNewInstanceWithEnvSetError,
    CLIBeekeeperLocallyAlreadyRunningError,
)
from clive.__private.core.commands.beekeeper import IsBeekeeperRunning
from clive.__private.core.constants.setting_identifiers import BEEKEEPER_REMOTE_ADDRESS, BEEKEEPER_SESSION_TOKEN
from clive.__private.settings import clive_prefixed_envvar, safe_settings


@dataclass(kw_only=True)
class BeekeeperInfo(WorldBasedCommand):
    """Display information about the Beekeeper session."""

    @property
    def should_require_unlocked_wallet(self) -> bool:
        """
        Checking if unlocked wallet should be required.

        Returns:
            bool: False, because this command does not require an unlocked wallet.
        """
        return False

    async def _run(self) -> None:
        """
        Run the command to display information about the Beekeeper session.

        This method retrieves the Beekeeper session information and prints it to the console.
        Information includes session details such as the session token, remote address, and other relevant data.

        Returns:
            None: This method does not return any value, it only prints the information into console.
        """
        session = await self.world.beekeeper_manager.beekeeper.session
        info = (await session.get_info()).json(by_alias=True)
        typer.echo(info)


@dataclass(kw_only=True)
class BeekeeperCreateSession(WorldBasedCommand):
    """
    Create a new Beekeeper session and display the session token.

    Args:
        echo_token_only (bool): If True, only the session token is printed. If False, additional information
            about how to use the session in the Clive CLI environment is provided.
    """

    echo_token_only: bool

    @property
    def should_validate_if_session_token_required(self) -> bool:
        """
        Check if the session token is required for this command.

        Returns:
            bool: False, because this command does not require a session token to be set.
        """
        return False

    @property
    def should_require_unlocked_wallet(self) -> bool:
        """
        Check if an unlocked wallet is required for this command.

        Returns:
            bool: False, because this command does not require an unlocked wallet.
        """
        return False

    async def _run(self) -> None:
        """
        Run the command to create a new Beekeeper session.

        This method creates a new session with the Beekeeper, retrieves the session token,
        and prints it to the console. If `echo_token_only` is set to True, only the token is printed.
        If `echo_token_only` is False, additional instructions on how to set the session token in the
        Clive CLI environment are provided.

        Returns:
            None: This method does not return any value, it only prints the session token or instructions into console.
        """
        session = await self.world.beekeeper_manager.beekeeper.create_session()
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

    async def _hook_before_entering_context_manager(self) -> None:
        """
        Display information about using Beekeeper if not using echo-token-only flag.

        Returns:
            None: This method does not return any value, it only prints information into console.
        """
        if not self.echo_token_only:
            await super()._hook_before_entering_context_manager()


@dataclass(kw_only=True)
class BeekeeperSpawn(ExternalCLICommand):
    """
    Spawn a new instance of Beekeeper and display its address and session token.

    Args:
        background: If True, the Beekeeper runs in the background.
        echo_address_only: If True, only the Beekeeper's address is printed. If False, additional information
            about how to use the Beekeeper in the Clive CLI environment is provided.
    """

    background: bool
    echo_address_only: bool

    async def validate(self) -> None:
        """
        Validate the environment before spawning a new Beekeeper instance.

        Returns:
            None: This method does not return any value, it only performs validation checks.
        """
        await self._validate_beekeepers_env_vars_not_set()
        await self._validate_beekeeper_is_not_running()
        await super().validate()

    async def _run(self) -> None:
        """
        Run the command to spawn a new Beekeeper instance.

        This method creates a new instance of Beekeeper, detaches it, and prints the address and session token.
        If `echo_address_only` is set to True, only the Beekeeper's address is printed.
        If `echo_address_only` is False, additional instructions on how to set the Beekeeper address and session token
        in the Clive CLI environment are provided.

        Returns:
            None: This method does not return any value,
            it only prints the Beekeeper's address and session token into console.
        """
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

        Raises:
            CLIBeekeeperCannotSpawnNewInstanceWithEnvSetError: If the environment variables for Beekeeper are set.

        Returns:
            None: This method does not return any value, it only performs validation checks.
        """
        if safe_settings.beekeeper.is_remote_address_set or safe_settings.beekeeper.is_session_token_set:
            raise CLIBeekeeperCannotSpawnNewInstanceWithEnvSetError

    async def _validate_beekeeper_is_not_running(self) -> None:
        """
        Validate that Beekeeper is not already running locally.

        Raises:
            CLIBeekeeperLocallyAlreadyRunningError: If Beekeeper is already running locally.

        Returns:
            None: This method does not return any value, it only performs validation checks.
        """
        result = await IsBeekeeperRunning().execute_with_result()
        if result.is_running:
            raise CLIBeekeeperLocallyAlreadyRunningError(result.pid_ensure)

    @staticmethod
    def __serve_forever() -> None:
        """
        Serve forever in the foreground, allowing the user to interact with the Beekeeper instance.

        This method runs an infinite loop, allowing the user to keep the Beekeeper instance running
        in the foreground. It prints a message indicating how to exit the loop.

        Returns:
            None: This method does not return any value, it only runs an infinite loop.
        """
        typer.echo("Press Ctrl+C to exit.")

        while True:
            time.sleep(1)


@dataclass(kw_only=True)
class BeekeeperClose(ExternalCLICommand):
    """Close the running Beekeeper instance."""

    async def _run(self) -> None:
        """
        Run the command to close the running Beekeeper instance.

        This method attempts to close the Beekeeper instance by calling the `close_already_running_beekeeper` function.
        If no Beekeeper instance is running, it catches the `FailedToDetectRunningBeekeeperError` and prints a message.
        If the Beekeeper instance is successfully closed, it prints a confirmation message.

        Raises:
            FailedToDetectRunningBeekeeperError: If no running Beekeeper instance is detected.

        Returns:
            None: This method does not return any value, it only prints messages into console.
        """
        typer.echo("Closing beekeeper...")
        beekeeper_working_directory = safe_settings.beekeeper.working_directory
        try:
            close_already_running_beekeeper(cwd=beekeeper_working_directory)
        except FailedToDetectRunningBeekeeperError:
            typer.echo("There was no running beekeeper.")
        else:
            typer.echo("Beekeeper was closed.")
