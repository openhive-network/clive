"""
Only common options (reusable or possibly reusable across multiple commands) should be defined here.

Do not place options that are specific to a single command here.
Options can have e.g. very command-specific help message and should not be defined here.
In such a situation, the option should be defined in the command module itself.
"""

from __future__ import annotations

from functools import partial

import typer

from clive.__private.cli.common.parameters.modified_param import modified_param
from clive.__private.cli.common.parsers import (
    decimal_percent,
    liquid_asset,
    voting_asset,
)
from clive.__private.core.constants.cli import (
    OPERATION_COMMON_OPTIONS_PANEL_TITLE,
    PAGE_NUMBER_OPTION_MINIMAL_VALUE,
    PAGE_SIZE_OPTION_MINIMAL_VALUE,
    PERFORM_WORKING_ACCOUNT_LOAD,
)

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
    ...,
    "--profile-name",
    help="The profile to use.",
)

account_name = modified_param(working_account_template, param_decls=("--account-name",))

new_account_name = typer.Option(
    ...,
    "--new-account-name",
    help="The name of the new account.",
)

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
)

liquid_amount = typer.Option(
    ...,
    "--amount",
    parser=liquid_asset,
    help="The liquid asset (HIVE/HBD) amount. (e.g. 2.500 HIVE)",
)

liquid_amount_optional = modified_param(liquid_amount, default=None)

voting_amount = typer.Option(
    ...,
    "--amount",
    parser=voting_asset,
    help="The voting asset (HP/VESTS) amount. (e.g. 2.500 HP)",
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

page_size = typer.Option(
    10,
    min=PAGE_SIZE_OPTION_MINIMAL_VALUE,
    help="The number of entries presented on a single page.",
)

page_no = typer.Option(
    0,
    min=PAGE_NUMBER_OPTION_MINIMAL_VALUE,
    help="Page number to display, considering the given page size.",
)

force_value = typer.Option(
    default=False,
    help=(
        "This flag is required when performing operations to exchange accounts.\n"
        "Some operations are not handled by exchanges.\n"
        "Use --force to explicitly confirm and proceed with the operation despite this limitation."
    ),
)

# OPERATION COMMON OPTIONS >>

_operation_common_option = partial(modified_param, rich_help_panel=OPERATION_COMMON_OPTIONS_PANEL_TITLE)

sign_with = _operation_common_option(typer.Option(None, help="Key alias to sign the transaction with."))
broadcast = _operation_common_option(
    typer.Option(default=True, help="Whether broadcast the transaction. (i.e. dry-run)")
)
save_file = _operation_common_option(
    typer.Option(
        None,
        help="The file to save the transaction to (format is determined by file extension - .bin or .json).",
    )
)
autosign = _operation_common_option(
    typer.Option(
        default=None,
        help=(
            "Whether to sign the transaction automatically, using single key from the profile as default one"
            " (if there are multiple keys, it will raise an error)."
        ),
        show_default=False,
    )
)

# << OPERATION COMMON OPTIONS
