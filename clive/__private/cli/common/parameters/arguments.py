from __future__ import annotations

import typer

from clive.__private.cli.common.parameters import modified_param
from clive.__private.cli.common.parameters.utils import get_default_or_make_optional, get_default_profile_name
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD, REQUIRED_AS_ARG_OR_OPTION

working_account_template = typer.Argument(
    PERFORM_WORKING_ACCOUNT_LOAD,  # we don't know if account_name_option is required until the profile is loaded
    help=f"The account to use. (default is working account of profile, {REQUIRED_AS_ARG_OR_OPTION})",
    show_default=False,
)

account_name = modified_param(working_account_template)
profile_name = typer.Argument(
    get_default_or_make_optional(get_default_profile_name()),
    help=f"The profile to use. (default is name of the default profile, {REQUIRED_AS_ARG_OR_OPTION})",
    show_default=bool(get_default_profile_name()),
)
