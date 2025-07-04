from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper

beekeeper = CliveTyper(name="beekeeper", help="Beekeeper-related commands.")


@beekeeper.command()
async def info() -> None:
    """
    Show the beekeeper info.

    Returns:
        None: This function does not return any value. It is used to display information about the beekeeper.
    """
    from clive.__private.cli.commands.beekeeper import BeekeeperInfo

    await BeekeeperInfo().run()


@beekeeper.command()
async def spawn(
    background: bool = typer.Option(default=True, help="Run in background."),  # noqa: FBT001
    echo_address_only: bool = typer.Option(default=False, help="Display only address of launched Beekeeper."),  # noqa: FBT001
) -> None:
    """
    Spawn beekeeper process.

    Args:
        background: If True, run the beekeeper in the background. Defaults to True.
        echo_address_only: If True, display only the address of the launched Beekeeper. Defaults to False.

    Returns:
        None: This function does not return any value. It is used to spawn the beekeeper process.
    """
    from clive.__private.cli.commands.beekeeper import BeekeeperSpawn

    await BeekeeperSpawn(background=background, echo_address_only=echo_address_only).run()


@beekeeper.command()
async def create_session(
    echo_token_only: bool = typer.Option(default=False, help="Display only token."),  # noqa: FBT001
) -> None:
    """
    Create beekeeper session.

    Args:
        echo_token_only: If True, display only the token of the created session. Defaults to False.

    Returns:
        None: This function does not return any value. It is used to create a session with the beekeeper.
    """
    from clive.__private.cli.commands.beekeeper import BeekeeperCreateSession

    await BeekeeperCreateSession(echo_token_only=echo_token_only).run()


@beekeeper.command()
async def close() -> None:
    """
    Close beekeeper process.

    Returns:
        None: This function does not return any value. It is used to close the beekeeper process.
    """
    from clive.__private.cli.commands.beekeeper import BeekeeperClose

    await BeekeeperClose().run()
