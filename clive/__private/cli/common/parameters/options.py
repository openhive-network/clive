"""
Only common options (reusable or possibly reusable across multiple commands) should be defined here.

Do not place options that are specific to a single command here.
Options can have e.g. very command-specific help message and should not be defined here.
In such a situation, the option should be defined in the command module itself.
"""

from __future__ import annotations

import typer

from clive.__private.cli.common.parameters.get_default import (
    get_default_beekeeper_remote,
    get_default_or_make_required,
    get_default_profile_name,
)
from clive.__private.cli.common.parameters.modified_param import (
    modified_param,
)
from clive.__private.cli.common.parsers import (
    decimal_percent,
    liquid_asset,
    voting_asset,
)
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD

working_account_template = typer.Option(
    PERFORM_WORKING_ACCOUNT_LOAD,  # we don't know if account_name_option is required until the profile is loaded
    help="The account to use. (default is working account of profile)",
    show_default=False,
)

working_account_list_template = typer.Option(
    [PERFORM_WORKING_ACCOUNT_LOAD],  # we don't know if account_name_option is required until the profile is loaded
    help="List of accounts to use. (default is working account of profile)",
    show_default=False,
)

profile_name = typer.Option(
    get_default_or_make_required(get_default_profile_name()),
    "--profile-name",
    help="The profile to use.",
    show_default=bool(get_default_profile_name()),
)

beekeeper_remote = typer.Option(
    ...,
    "--beekeeper-remote",
    default_factory=lambda: get_default_beekeeper_remote(),
    help="Beekeeper remote endpoint. (starts locally if not provided)",
    show_default=False,
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

liquid_amount = typer.Option(
    ...,
    "--amount",
    parser=liquid_asset,
    help="The liquid asset (HIVE/HBD) amount. (e.g. 2.500 HIVE)",
    show_default=False,
)

liquid_amount_optional = modified_param(liquid_amount, default=None)

voting_amount = typer.Option(
    ...,
    "--amount",
    parser=voting_asset,
    help="The voting asset (HP/VESTS) amount. (e.g. 2.500 HP)",
    show_default=False,
)

percent = typer.Option(
    ...,
    "--percent",
    parser=decimal_percent,
    help="Percent (0.00-100.00)",
)

memo_value = typer.Option(
    "",
    "--memo",
    help="The memo to attach to the transfer.",
)
memo_value_optional = modified_param(memo_value, default=None)
