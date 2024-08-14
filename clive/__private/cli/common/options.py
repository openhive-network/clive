from __future__ import annotations

import contextlib
from copy import deepcopy
from typing import TYPE_CHECKING, Any

import typer

from clive.__private.cli.common.parsers import (
    decimal_percent,
    liquid_asset,
    scheduled_transfer_frequency_parser,
    voting_asset,
)
from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD
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
        from clive.__private.core.profile import Profile
        from clive.__private.storage.service import NoDefaultProfileToLoadError

        with contextlib.suppress(NoDefaultProfileToLoadError):
            return Profile.get_default_profile_name()
    return None


def _get_default_working_account_name() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.profile import Profile, ProfileError

        with contextlib.suppress(ProfileError):
            return Profile.load(auto_create=False).accounts.working.name
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
    "--profile-name",
    help="The profile to use.",
    show_default=bool(_get_default_profile_name()),
)

password_option = typer.Option(..., "--password", help="Password to unlock the wallet.", show_default=False)

password_optional_option = modified_option(password_option, default=None)


# we don't know if account_name_option is required until the profile is loaded
working_account_option_template = typer.Option(
    PERFORM_WORKING_ACCOUNT_LOAD,
    help="The account to use. (default is working account of profile)",
    show_default=False,
)

beekeeper_remote_option = typer.Option(
    _get_default_beekeeper_remote(),
    "--beekeeper-remote",
    help="Beekeeper remote endpoint. (starts locally if not provided)",
    show_default=bool(_get_default_beekeeper_remote()),
)

account_name_option = modified_option(
    working_account_option_template,
    param_decls=("--account-name",),
)

from_account_name_option = modified_option(
    working_account_option_template,
    param_decls=("--from",),
    help='The account to use as "from" argument. (default is working account of profile)',
)

to_account_name_option = modified_option(
    working_account_option_template,
    param_decls=("--to",),
    help='The account to use as "to" argument. (default is working account of profile)',
)

to_account_name_no_default_option = typer.Option(
    ...,
    "--to",
    help='The account to use as "to" argument.',
    show_default=False,
)

delegatee_account_name_option = typer.Option(
    ...,
    "--delegatee",
    help='The account to use as "delegatee" argument.',
    show_default=False,
)

proposal_id: list[int] = typer.Option(
    ...,
    "--proposal-id",
    help=f"List of proposal identifiers, option can appear {MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION} times.",
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
    "--amount",
    parser=liquid_asset,
    help="The liquid asset (HIVE/HBD) amount to transfer. (e.g. 2.500 HIVE)",
    show_default=False,
)

liquid_amount_optional_option = modified_option(liquid_amount_option, default=None)

frequency_value_option = typer.Option(
    ...,
    "--frequency",
    parser=scheduled_transfer_frequency_parser,
    help=f"How often the transfer should be executed ({SHORTHAND_TIMEDELTA_EXAMPLE})",
    show_default=False,
)
frequency_value_optional_option = modified_option(frequency_value_option, default=None)

memo_value_option = typer.Option(
    "",
    "--memo",
    help="The memo to attach to the transfer.",
)
memo_value_optional_option = modified_option(memo_value_option, default=None)


pair_id_value_option = typer.Option(
    0,
    "--pair-id",
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
    "--repeat",
    min=SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE,
    help="How many times the recurrent transfer should be executed. (must be greater than 1)",
    show_default=False,
)
repeat_value_optional_option = modified_option(repeat_value_option, default=None)


voting_amount_option = typer.Option(
    ...,
    "--amount",
    parser=voting_asset,
    help="The voting asset (HP/VESTS). (e.g. 2.500 HP)",
    show_default=False,
)

percent_option = typer.Option(
    ...,
    "--percent",
    parser=decimal_percent,
    help="Percent (0.00-100.00)",
)

working_account_list_option_template = typer.Option(
    [PERFORM_WORKING_ACCOUNT_LOAD],
    help="List of accounts to use. (default is working account of profile)",
    show_default=False,
)
