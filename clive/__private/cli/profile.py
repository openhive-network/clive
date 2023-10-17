import typer

from clive.__private.cli.common import options
from clive.__private.core._async import asyncio_run

profile_ = typer.Typer(help="Manage your profile.")


@profile_.command()
def show(
    profile: str = options.profile_option,
) -> None:
    """Show profile information."""
    from clive.__private.cli.commands.profile import ProfileShow

    asyncio_run(ProfileShow(profile=profile).run())


@profile_.command()
def list_all() -> None:
    """List all stored profiles."""
    from clive.__private.cli.commands.profile import ProfileList

    asyncio_run(ProfileList().run())


@profile_.command()
def create(
    name: str = typer.Option(..., help="The name of the profile.", show_default=False),
) -> None:
    """Create a new profile."""
    from clive.__private.cli.commands.profile import ProfileCreate

    asyncio_run(ProfileCreate(name=name).run())
