from __future__ import annotations

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common.parameters import argument_related_options, modified_param
from clive.__private.cli.common.parameters.ensure_single_value import EnsureSingleProfileNameValue
from clive.__private.core.constants.cli import REQUIRED_AS_ARG_OR_OPTION

profile = CliveTyper(name="profile", help="Manage your Clive profile(s).")

_profile_name_create_argument = typer.Argument(
    None,
    help=f"The name of the new profile. ({REQUIRED_AS_ARG_OR_OPTION})",
    show_default=False,
)


@profile.command(name="create")
async def create_profile(
    profile_name: str | None = _profile_name_create_argument,
    profile_name_option: str | None = argument_related_options.profile_name,
    working_account_name: str | None = typer.Option(None, help="The name of the working account.", show_default=False),
) -> None:
    """
    Create a new profile. Password for new profile is provided by stdin.

    If new password is entered in terminal it must be repeated.
    """
    from clive.__private.cli.commands.configure.profile import CreateProfile  # noqa: PLC0415

    await CreateProfile(
        profile_name=EnsureSingleProfileNameValue().of(profile_name, profile_name_option),
        working_account_name=working_account_name,
    ).run()


_profile_name_delete_argument = modified_param(
    _profile_name_create_argument, help=f"The name of the profile to delete. ({REQUIRED_AS_ARG_OR_OPTION})"
)


@profile.command(name="delete")
async def delete_profile(
    profile_name: str = _profile_name_delete_argument,
    profile_name_option: str | None = argument_related_options.profile_name,
    force: bool = typer.Option(  # noqa: FBT001
        default=False,
        help="Force delete all profile data (including different versions and backups)",
    ),
) -> None:
    """Delete a profile."""
    from clive.__private.cli.commands.configure.profile import DeleteProfile  # noqa: PLC0415

    await DeleteProfile(
        profile_name=EnsureSingleProfileNameValue().of(profile_name, profile_name_option),
        force=force,
    ).run()
