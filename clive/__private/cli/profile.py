from typing import Optional

import typer

from clive.__private.cli.common import WithBeekeeper, options
from clive.__private.cli.common.with_profile import WithProfile
from clive.__private.core._async import asyncio_run

profile = typer.Typer(name="profile", help="Manage your profile.")


@profile.command()
@WithProfile.decorator
async def show(ctx: typer.Context) -> None:
    """Show profile information."""
    from clive.__private.cli.commands.profile import ProfileShow

    common = WithProfile(**ctx.params)
    await ProfileShow(profile_data=common.profile_data).run()


@profile.command()
def list_all() -> None:
    """List all stored profiles."""
    from clive.__private.cli.commands.profile import ProfileList

    asyncio_run(ProfileList().run())


@profile.command()
@WithBeekeeper.decorator
async def create(
    ctx: typer.Context,
    profile_name: str = typer.Option(..., help="The name of the new profile.", show_default=False),
    password: str = options.password_option,
    working_account_name: Optional[str] = typer.Option(
        None, help="The name of the working account.", show_default=False
    ),
) -> None:
    """Create a new profile."""
    from clive.__private.cli.commands.profile import ProfileCreate

    common = WithBeekeeper(**ctx.params)
    await ProfileCreate(
        beekeeper=common.beekeeper,
        profile_name=profile_name,
        password=password,
        working_account_name=working_account_name,
    ).run()


@profile.command()
def switch(
    profile_name: str = typer.Option(..., help="The name of the profile to switch to.", show_default=False),
) -> None:
    """Switch to a profile."""
    from clive.__private.cli.commands.profile import ProfileSwitch

    asyncio_run(ProfileSwitch(profile_name=profile_name).run())


@profile.command()
def delete(
    profile_name: str = typer.Option(..., help="The name of the profile to delete.", show_default=False),
) -> None:
    """Delete a profile."""
    from clive.__private.cli.commands.profile import ProfileDelete

    asyncio_run(ProfileDelete(profile_name=profile_name).run())


@profile.command()
@WithProfile.decorator
async def set_node(
    ctx: typer.Context,
    node_address: str = typer.Option(..., help="The address of the node to use.", show_default=False),
) -> None:
    """Set the node address for the profile."""
    from clive.__private.cli.commands.profile import ProfileSetNode

    common = WithProfile(**ctx.params)
    await ProfileSetNode(profile_data=common.profile_data, node_address=node_address).run()
