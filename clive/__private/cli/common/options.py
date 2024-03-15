from __future__ import annotations

import contextlib
from copy import deepcopy
from typing import TYPE_CHECKING, Any

import typer

from clive.__private.cli.common.asset_parsers import liquid_asset, voting_asset
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.core.constants import MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION

if TYPE_CHECKING:
    from typer.models import OptionInfo


def _get_default_profile_name() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.profile_data import NoDefaultProfileToLoadError, ProfileData

        with contextlib.suppress(NoDefaultProfileToLoadError):
            return ProfileData.get_default_profile_name()
    return None


def _get_default_working_account_name() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.profile_data import ProfileData, ProfileDataError

        with contextlib.suppress(ProfileDataError):
            return ProfileData.load(auto_create=False).working_account.name
    return None


def _get_default_beekeeper_remote() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.beekeeper import Beekeeper

        address = Beekeeper.get_remote_address_from_settings() or Beekeeper.get_remote_address_from_connection_file()
        return str(address) if address else None
    return None


def get_default_or_make_required(value: Any) -> Any:
    return ... if value is None else value


def modified_option(option: OptionInfo, **kwargs: Any) -> Any:
    """
    Create option based on another option, but with some attributes modified.

    Args:
    ----
    option: The option to modify.
    kwargs: The attributes to modify.
    """
    new_option = deepcopy(option)
    for key, value in kwargs.items():
        if not hasattr(new_option, key):
            raise ValueError(f"Unknown option attribute: {key}\navailable attributes: {list(option.__dict__)}")
        setattr(new_option, key, value)
    return new_option


profile_name_option = typer.Option(
    get_default_or_make_required(_get_default_profile_name()),
    help="The profile to use.",
    show_default=bool(_get_default_profile_name()),
)

password_option = typer.Option(..., help="Password to unlock the wallet.", show_default=False)

password_optional_option = modified_option(password_option, default=None)

account_name_option = typer.Option(
    get_default_or_make_required(_get_default_working_account_name()),
    help="The account to use. (defaults to the working account of the default profile)",
    show_default=bool(_get_default_working_account_name()),
)

beekeeper_remote_option = typer.Option(
    _get_default_beekeeper_remote(),
    help="Beekeeper remote endpoint. (starts locally if not provided)",
    show_default=bool(_get_default_beekeeper_remote()),
)

from_account_name_option = typer.Option(
    get_default_or_make_required(_get_default_working_account_name()),
    "--from",
    help='The account to use as "from" argument. (defaults to the working account of the last used profile)',
    show_default=bool(_get_default_working_account_name()),
)

to_account_name_option = typer.Option(
    get_default_or_make_required(_get_default_working_account_name()),
    "--to",
    help='The account to use as "to" argument. (defaults to the working account of the last used profile)',
    show_default=bool(_get_default_working_account_name()),
)

to_account_name_no_default_option = typer.Option(
    ...,
    "--to",
    help='The account to use as "to" argument.',
    show_default=False,
)

delegatee_account_name_option = typer.Option(
    ...,
    help='The account to use as "delegatee" argument.',
    show_default=False,
)

proposal_id: list[int] = typer.Option(
    ..., help=f"List of proposal identifiers, option can appear {MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION} times."
)

authority_account_name_option = typer.Option(
    ...,
    "--account",
    help="The account to  add/remove/modify (account must exist).",
    show_default=False,
)

authority_key_option = typer.Option(
    ...,
    "--key",
    help="The public key to add/remove/modify",
    show_default=False,
)

authority_weight_option = typer.Option(
    ...,
    "--weight",
    help="The new weight of account/key authority",
    show_default=False,
)

liquid_amount_option = typer.Option(
    ...,
    parser=liquid_asset,
    help="The liquid asset (HIVE/HBD) amount to transfer. (e.g. 2.500 HIVE)",
    show_default=False,
)

voting_amount_option = typer.Option(
    ...,
    parser=voting_asset,
    help="The voting asset (HIVE/VESTS). (e.g. 2.500 HIVE)",
    show_default=False,
)
