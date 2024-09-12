from __future__ import annotations

from typing import TYPE_CHECKING, Any

import typer

from clive.__private.cli.common.parameters.modified_param import modified_param
from clive.__private.cli.common.parameters import options
from clive.__private.core.constants.cli import LOOK_INTO_ARGUMENT_OPTION_HELP

if TYPE_CHECKING:
    from typer.models import OptionInfo


def make_argument_related_option(source: str | OptionInfo) -> Any:  # noqa: ANN401
    """
    Create an argument related option based on another option or create a new one.

    Args:
    ----
    source: The option to modify or param_decls of the new option.
    """
    if isinstance(source, str):
        return typer.Option(None, source, show_default=False, help=LOOK_INTO_ARGUMENT_OPTION_HELP)
    return modified_param(source, default=None, show_default=False, help=LOOK_INTO_ARGUMENT_OPTION_HELP)


account_name = make_argument_related_option(options.account_name)

profile_name = make_argument_related_option(options.profile_name)

password = make_argument_related_option(options.password)
