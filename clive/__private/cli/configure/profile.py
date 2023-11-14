from typing import Optional

import typer

from clive.__private.cli.common import BeekeeperCommonOptions, options
from clive.__private.core._async import asyncio_run

profile = typer.Typer(name="profile", help="Manage your Clive profile(s).")


@profile.command(name="add")
@BeekeeperCommonOptions.decorator
async def create_profile(
    ctx: typer.Context,
    profile_name: str = typer.Option(..., help="The name of the new profile.", show_default=False),
    password: str = options.password_option,
    working_account_name: Optional[str] = typer.Option(
        None, help="The name of the working account.", show_default=False
    ),
) -> None:
    """Create a new profile."""
    from clive.__private.cli.commands.configure.profile import CreateProfile

    common = BeekeeperCommonOptions(**ctx.params)
    await CreateProfile(
        **common.dict(),
        profile_name=profile_name,
        password=password,
        working_account_name=working_account_name,
    ).run()


@profile.command(name="set-default")
def set_default_profile(
    profile_name: str = typer.Option(..., help="The name of the profile to switch to.", show_default=False),
) -> None:
    """Set the profile which will be used by default in all profile-related commands."""
    from clive.__private.cli.commands.configure.profile import SetDefaultProfile

    asyncio_run(SetDefaultProfile(profile_name=profile_name).run())


@profile.command(name="remove")
def delete_profile(
    profile_name: str = typer.Option(..., help="The name of the profile to delete.", show_default=False),
) -> None:
    """Delete a profile."""
    from clive.__private.cli.commands.configure.profile import DeleteProfile

    asyncio_run(DeleteProfile(profile_name=profile_name).run())
