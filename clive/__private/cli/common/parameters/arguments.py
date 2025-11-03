"""
Only common arguments (reusable or possibly reusable across multiple commands) should be defined here.

Do not place arguments that are specific to a single command here.
Arguments can have e.g. very command-specific help message and should not be defined here.
In such a situation, the argument should be defined in the command module itself.
"""

from __future__ import annotations

import typer

from clive.__private.cli.common.parameters import modified_param
from clive.__private.cli.common.parsers import public_key, public_key_or_account_with_weight
from clive.__private.core.constants.cli import (
    KEY_OR_ACCOUNT_WITH_WEIGHT_METAVAR,
    PERFORM_WORKING_ACCOUNT_LOAD,
    REQUIRED_AS_ARG_OR_OPTION,
)

working_account_template = typer.Argument(
    PERFORM_WORKING_ACCOUNT_LOAD,  # we don't know if account_name_option is required until the profile is loaded
    help=f"The account to use. (default is working account of profile, {REQUIRED_AS_ARG_OR_OPTION})",
    show_default=False,
)

account_name = modified_param(working_account_template)

profile_name = typer.Argument(..., help=f"The profile to use. ({REQUIRED_AS_ARG_OR_OPTION})")

owner_key_or_account = typer.Argument(
    None,
    parser=public_key_or_account_with_weight,
    help=(
        f"Owner public key or account with optional weight that will be set for account. ({REQUIRED_AS_ARG_OR_OPTION})"
    ),
    metavar=KEY_OR_ACCOUNT_WITH_WEIGHT_METAVAR,
)

active_key_or_account = typer.Argument(
    None,
    parser=public_key_or_account_with_weight,
    help=(
        f"Active public key or account with optional weight that will be set for account. ({REQUIRED_AS_ARG_OR_OPTION})"
    ),
    metavar=KEY_OR_ACCOUNT_WITH_WEIGHT_METAVAR,
)

posting_key_or_account = typer.Argument(
    None,
    parser=public_key_or_account_with_weight,
    help=(
        "Posting public key or account with optional weight"
        f" that will be set for account. ({REQUIRED_AS_ARG_OR_OPTION})"
    ),
    metavar=KEY_OR_ACCOUNT_WITH_WEIGHT_METAVAR,
)

memo_key = typer.Argument(
    None,
    parser=public_key,
    help=f"Memo public key that will be set for account. ({REQUIRED_AS_ARG_OR_OPTION})",
)
