from __future__ import annotations

import contextlib
from copy import deepcopy
from typing import TYPE_CHECKING, Any

import typer

from clive.__private.cli.common.parsers import (
    decimal_percent,
    liquid_asset,
    smart_frequency_parser,
    voting_asset,
)
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.core.constants.node import (
    MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION,
    SCHEDULED_TRANSFER_MINIMUM_PAIR_ID_VALUE,
    SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE,
)
from clive.__private.core.shorthand_timedelta import SHORTHAND_TIMEDELTA_EXAMPLE

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


def get_default_or_make_required(value: Any) -> Any:  # noqa: ANN401
    return ... if value is None else value


def modified_option(option: OptionInfo, **kwargs: Any) -> Any:  # noqa: ANN401
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

liquid_amount_optional_option = modified_option(liquid_amount_option, default=None)

frequency_value_option = typer.Option(
    ...,
    parser=smart_frequency_parser,
    help=(
        "How often the transfer should be executed "
        f"(hH - hours, dD - days, wW - weeks {SHORTHAND_TIMEDELTA_EXAMPLE})"
    ),
    show_default=False,
)
frequency_value_optional_option = modified_option(frequency_value_option, default=None)

memo_value_option = typer.Option("", help="The memo to attach to the transfer.")
memo_value_optional_option = modified_option(memo_value_option, default=None)


pair_id_value_option = typer.Option(
    0,
    min=SCHEDULED_TRANSFER_MINIMUM_PAIR_ID_VALUE,
    help=(
        "Unique pair id used to differentiate between multiple transfers to the same account \n"
        "(will be mandatory since HF28)."
    ),
    show_default=True,
)
pair_id_value_none_option = modified_option(pair_id_value_option, default=None, show_default=False)

repeat_value_option = typer.Option(
    ...,
    min=SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE,
    help="How many times the recurrent transfer should be executed. (must be greater than 1)",
    show_default=False,
)
repeat_value_optional_option = modified_option(repeat_value_option, default=None)


voting_amount_option = typer.Option(
    ...,
    parser=voting_asset,
    help="The voting asset (HP/VESTS). (e.g. 2.500 HP)",
    show_default=False,
)

percent_option = typer.Option(
    ...,
    parser=decimal_percent,
    help="Percent (0.00-100.00)",
)
