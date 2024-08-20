from __future__ import annotations

import typer

from clive.__private.cli.common.parameters import modified_param
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD, REQUIRED_AS_ARG_OR_OPTION

# we don't know if account_name_option is required until the profile is loaded
working_account_argument_template = typer.Argument(
    PERFORM_WORKING_ACCOUNT_LOAD,
    help=f"The account to use. (default is working account of profile, {REQUIRED_AS_ARG_OR_OPTION})",
    show_default=False,
)

account_name_argument = modified_param(working_account_argument_template)
