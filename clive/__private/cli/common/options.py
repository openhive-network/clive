from typing import Any

import typer

from clive.__private.cli.completion import is_tab_completion_active


def _get_default_profile_name() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.profile_data import ProfileData

        return ProfileData.get_lastly_used_profile_name()
    return None


def _get_default_working_account_name() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.profile_data import ProfileData, ProfileDataError

        try:
            return ProfileData.load(auto_create=False).working_account.name
        except ProfileDataError:
            return None
    return None


def _get_default_beekeeper_remote() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.beekeeper import Beekeeper

        address = Beekeeper.get_remote_address_from_settings() or Beekeeper.get_remote_address_from_connection_file()
        return str(address) if address else None
    return None


def get_default_or_make_required(value: Any) -> Any:
    return ... if value is None else value


profile_name_option = typer.Option(
    get_default_or_make_required(_get_default_profile_name()),
    help="The profile to use. (defaults to the last used profile)",
    show_default=bool(_get_default_profile_name()),
)

password_option = typer.Option(..., help="Password to unlock the wallet.", show_default=False)

account_name_option = typer.Option(
    get_default_or_make_required(_get_default_working_account_name()),
    help="The account to use. (defaults to the working account of the last used profile)",
    show_default=bool(_get_default_working_account_name()),
)

beekeeper_remote_option = typer.Option(
    _get_default_beekeeper_remote(),
    help="Beekeeper remote endpoint. (starts locally if not provided)",
    show_default=bool(_get_default_beekeeper_remote()),
)
