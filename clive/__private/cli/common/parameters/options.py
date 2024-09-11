from __future__ import annotations

import typer

from clive.__private.cli.common.parameters.utils import (
    get_default_beekeeper_remote,
    get_default_or_make_required,
    get_default_profile_name,
    modified_param,
)
from clive.__private.cli.common.parsers import (
    decimal_percent,
    liquid_asset,
    scheduled_transfer_frequency_parser,
    voting_asset,
)
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD
from clive.__private.core.constants.node import (
    MAX_NUMBER_OF_PROPOSAL_IDS_IN_SINGLE_OPERATION,
    SCHEDULED_TRANSFER_MINIMUM_PAIR_ID_VALUE,
    SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE,
)
from clive.__private.core.shorthand_timedelta import SHORTHAND_TIMEDELTA_EXAMPLE

profile_name = typer.Option(
    get_default_or_make_required(get_default_profile_name()),
    "--profile-name",
    help="The profile to use.",
    show_default=bool(get_default_profile_name()),
)

password = typer.Option(..., "--password", help="Password to unlock the wallet.", show_default=False)

password_optional = modified_param(password, default=None)

# we don't know if account_name_option is required until the profile is loaded
working_account_template = typer.Option(
    PERFORM_WORKING_ACCOUNT_LOAD,
    help="The account to use. (default is working account of profile)",
    show_default=False,
)

beekeeper_remote = typer.Option(
    get_default_beekeeper_remote(),
    "--beekeeper-remote",
    help="Beekeeper remote endpoint. (starts locally if not provided)",
    show_default=bool(get_default_beekeeper_remote()),
)

account_name = modified_param(working_account_template, param_decls=("--account-name",))

from_account_name = modified_param(
    working_account_template,
    param_decls=("--from",),
    help='The account to use as "from" argument. (default is working account of profile)',
)

to_account_name = modified_param(
    working_account_template,
    param_decls=("--to",),
    help='The account to use as "to" argument. (default is working account of profile)',
)

to_account_name_required = typer.Option(
    ...,
    "--to",
    help='The account to use as "to" argument.',
    show_default=False,
)

delegatee_account_name = typer.Option(
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

authority_account_name = typer.Option(
    ...,
    "--account",
    help="The account to  add/remove/modify (account must exist).",
    show_default=False,
)

authority_key = typer.Option(
    ...,
    "--key",
    help="The public key to add/remove/modify",
    show_default=False,
)

authority_weight = typer.Option(
    ...,
    "--weight",
    help="The new weight of account/key authority",
    show_default=False,
)

liquid_amount = typer.Option(
    ...,
    "--amount",
    parser=liquid_asset,
    help="The liquid asset (HIVE/HBD) amount to transfer. (e.g. 2.500 HIVE)",
    show_default=False,
)

liquid_amount_optional = modified_param(liquid_amount, default=None)

frequency_value = typer.Option(
    ...,
    "--frequency",
    parser=scheduled_transfer_frequency_parser,
    help=f"How often the transfer should be executed ({SHORTHAND_TIMEDELTA_EXAMPLE})",
    show_default=False,
)
frequency_value_optional = modified_param(frequency_value, default=None)

memo_value = typer.Option(
    "",
    "--memo",
    help="The memo to attach to the transfer.",
)
memo_value_optional = modified_param(memo_value, default=None)

pair_id_value = typer.Option(
    0,
    "--pair-id",
    min=SCHEDULED_TRANSFER_MINIMUM_PAIR_ID_VALUE,
    help=(
        "Unique pair id used to differentiate between multiple transfers to the same account \n"
        "(will be mandatory since HF28)."
    ),
    show_default=True,
)
pair_id_value_none = modified_param(pair_id_value, default=None, show_default=False)

repeat_value = typer.Option(
    ...,
    "--repeat",
    min=SCHEDULED_TRANSFER_MINIMUM_REPEAT_VALUE,
    help="How many times the recurrent transfer should be executed. (must be greater than 1)",
    show_default=False,
)
repeat_value_optional = modified_param(repeat_value, default=None)

voting_amount = typer.Option(
    ...,
    "--amount",
    parser=voting_asset,
    help="The voting asset (HP/VESTS). (e.g. 2.500 HP)",
    show_default=False,
)

percent = typer.Option(
    ...,
    "--percent",
    parser=decimal_percent,
    help="Percent (0.00-100.00)",
)

working_account_list_template = typer.Option(
    [PERFORM_WORKING_ACCOUNT_LOAD],
    help="List of accounts to use. (default is working account of profile)",
    show_default=False,
)
