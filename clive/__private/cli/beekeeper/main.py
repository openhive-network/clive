from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper

beekeeper = CliveTyper(name="beekeeper", help="Beekeeper-related commands.")


@beekeeper.command()
async def info() -> None:
    """Show the beekeeper info."""
    from clive.__private.cli.commands.beekeeper.beekeeper_info import BeekeeperInfo  # noqa: PLC0415

    await BeekeeperInfo().run()


@beekeeper.command()
async def spawn(
    background: bool = typer.Option(default=True, help="Run in background."),  # noqa: FBT001
    echo_address_only: bool = typer.Option(default=False, help="Display only address of launched Beekeeper."),  # noqa: FBT001
) -> None:
    """Spawn beekeeper process."""
    from clive.__private.cli.commands.beekeeper.beekeeper_spawn import BeekeeperSpawn  # noqa: PLC0415

    await BeekeeperSpawn(background=background, echo_address_only=echo_address_only).run()


@beekeeper.command()
async def create_session(
    echo_token_only: bool = typer.Option(default=False, help="Display only token."),  # noqa: FBT001
) -> None:
    """Create beekeeper session."""
    from clive.__private.cli.commands.beekeeper.beekeeper_create_session import BeekeeperCreateSession  # noqa: PLC0415

    await BeekeeperCreateSession(echo_token_only=echo_token_only).run()


@beekeeper.command()
async def close() -> None:
    """Close beekeeper process."""
    from clive.__private.cli.commands.beekeeper.beekeeper_close import BeekeeperClose  # noqa: PLC0415

    await BeekeeperClose().run()
