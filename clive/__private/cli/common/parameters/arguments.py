"""
Only common arguments (reusable or possibly reusable across multiple commands) should be defined here.

Do not place arguments that are specific to a single command here.
Arguments can have e.g. very command-specific help message and should not be defined here.
In such a situation, the argument should be defined in the command module itself.
"""

from __future__ import annotations

import typer

from clive.__private.cli.common.parameters import modified_param
from clive.__private.cli.common.parameters.styling import stylized_help
from clive.__private.cli.common.parsers import public_key
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD

working_account_template = typer.Argument(
    PERFORM_WORKING_ACCOUNT_LOAD,  # we don't know if account_name_option is required until the profile is loaded
    help=stylized_help("The account to use.", is_working_account_default=True, required_as_arg_or_option=True),
    show_default=False,
)

account_name = modified_param(working_account_template)

profile_name = typer.Argument(..., help=stylized_help("The profile to use.", required_as_arg_or_option=True))

owner = typer.Argument(
    None,
    parser=public_key,
    help=stylized_help("Owner public key that will be set for account.", required_as_arg_or_option=True),
)

active = typer.Argument(
    None,
    parser=public_key,
    help=stylized_help("Active public key that will be set for account.", required_as_arg_or_option=True),
)

posting = typer.Argument(
    None,
    parser=public_key,
    help=stylized_help("Posting public key that will be set for account.", required_as_arg_or_option=True),
)

memo_key = typer.Argument(
    None,
    parser=public_key,
    help=stylized_help("Memo public key that will be set for account.", required_as_arg_or_option=True),
)
