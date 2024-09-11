from typing import Optional

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import BeekeeperCommonOptions, options

profile = CliveTyper(name="profile", help="Manage your Clive profile(s).")


@profile.command(name="add", common_options=[BeekeeperCommonOptions])
async def create_profile(
    ctx: typer.Context,  # noqa: ARG001
    profile_name: str = typer.Option(..., help="The name of the new profile.", show_default=False),
    password: str = options.password,
    working_account_name: Optional[str] = typer.Option(
        None, help="The name of the working account.", show_default=False
    ),
) -> None:
    """Create a new profile."""
    from clive.__private.cli.commands.configure.profile import CreateProfile

    common = BeekeeperCommonOptions.get_instance()
    await CreateProfile(
        **common.as_dict(),
        profile_name=profile_name,
        password=password,
        working_account_name=working_account_name,
    ).run()


@profile.command(name="set-default")
async def set_default_profile(
    profile_name: str = typer.Option(..., help="The name of the profile to switch to.", show_default=False),
) -> None:
    """Set the profile which will be used by default in all profile-related commands."""
    from clive.__private.cli.commands.configure.profile import SetDefaultProfile

    await SetDefaultProfile(profile_name=profile_name).run()


@profile.command(name="remove")
async def delete_profile(
    profile_name: str = typer.Option(..., help="The name of the profile to delete.", show_default=False),
) -> None:
    """Delete a profile."""
    from clive.__private.cli.commands.configure.profile import DeleteProfile

    await DeleteProfile(profile_name=profile_name).run()
