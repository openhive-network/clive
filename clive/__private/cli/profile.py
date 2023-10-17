import typer

from clive.__private.cli.common import options
from clive.__private.core._async import asyncio_run

profile_ = typer.Typer(help="Manage your profile.")


@profile_.command()
def show(
    profile_name: str = options.profile_name_option,
) -> None:
    """Show profile information."""
    from clive.__private.cli.commands.profile import ProfileShow

    asyncio_run(ProfileShow(profile_name=profile_name).run())


@profile_.command()
def list_all() -> None:
    """List all stored profiles."""
    from clive.__private.cli.commands.profile import ProfileList

    asyncio_run(ProfileList().run())


@profile_.command()
def create(
    profile_name: str = typer.Option(..., help="The name of the new profile.", show_default=False),
) -> None:
    """Create a new profile."""
    from clive.__private.cli.commands.profile import ProfileCreate

    asyncio_run(ProfileCreate(profile_name=profile_name).run())
