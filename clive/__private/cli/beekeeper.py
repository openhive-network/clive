import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import BeekeeperOptionsGroup

beekeeper = CliveTyper(name="beekeeper", help="Beekeeper-related commands.")


@beekeeper.command(param_groups=[BeekeeperOptionsGroup])
async def info(ctx: typer.Context) -> None:  # noqa: ARG001
    """Show the beekeeper info."""
    from clive.__private.cli.commands.beekeeper import BeekeeperInfo

    common = BeekeeperOptionsGroup.get_instance()
    await BeekeeperInfo(**common.as_dict()).run()


@beekeeper.command()
async def spawn(
    background: bool = typer.Option(default=True, help="Run in background."),  # noqa: FBT001
    echo_address_only: bool = typer.Option(default=False, help="Display only address of launched Beekeeper."),  # noqa: FBT001
) -> None:
    """Spawn beekeeper process."""
    from clive.__private.cli.commands.beekeeper import BeekeeperSpawn

    await BeekeeperSpawn(background=background, echo_address_only=echo_address_only).run()


@beekeeper.command(param_groups=[BeekeeperOptionsGroup])
async def create_session(
    ctx: typer.Context,  # noqa: ARG001
    echo_token_only: bool = typer.Option(default=False, help="Display only token."),  # noqa: FBT001
) -> None:
    """Create beekeeper session."""
    from clive.__private.cli.commands.beekeeper import BeekeeperCreateSession

    common = BeekeeperOptionsGroup.get_instance()
    await BeekeeperCreateSession(**common.as_dict(), echo_token_only=echo_token_only).run()


@beekeeper.command()
async def close() -> None:
    """Close beekeeper process."""
    from clive.__private.cli.commands.beekeeper import BeekeeperClose

    await BeekeeperClose().run()
