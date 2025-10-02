"""
Only common arguments (reusable or possibly reusable across multiple commands) should be defined here.

Do not place arguments that are specific to a single command here.
Arguments can have e.g. very command-specific help message and should not be defined here.
In such a situation, the argument should be defined in the command module itself.
"""

from __future__ import annotations

import typer

from clive.__private.cli.common.parameters import modified_param
from clive.__private.cli.common.parsers import public_key
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD, REQUIRED_AS_ARG_OR_OPTION

working_account_template = typer.Argument(
    PERFORM_WORKING_ACCOUNT_LOAD,  # we don't know if account_name_option is required until the profile is loaded
    help=f"The account to use. (default is working account of profile, {REQUIRED_AS_ARG_OR_OPTION})",
    show_default=False,
)

account_name = modified_param(working_account_template)

profile_name = typer.Argument(..., help=f"The profile to use. ({REQUIRED_AS_ARG_OR_OPTION}")

owner_key = typer.Argument(
    None,
    parser=public_key,
    help=f"Owner public key that will be set for account. ({REQUIRED_AS_ARG_OR_OPTION})",
)

active_key = typer.Argument(
    None,
    parser=public_key,
    help=f"Active public key that will be set for account. ({REQUIRED_AS_ARG_OR_OPTION})",
)

posting_key = typer.Argument(
    None,
    parser=public_key,
    help=f"Posting public key that will be set for account. ({REQUIRED_AS_ARG_OR_OPTION})",
)

memo_key = typer.Argument(
    None,
    parser=public_key,
    help=f"Memo public key that will be set for account. ({REQUIRED_AS_ARG_OR_OPTION})",
)
