"""
All argument-related options should be defined here.

Argument related options are not command-specific.
That's because they don't contain anything command-specific like e.g. help message.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import typer

from clive.__private.cli.common.parameters import options
from clive.__private.cli.common.parameters.modified_param import modified_param
from clive.__private.core.constants.cli import LOOK_INTO_ARGUMENT_OPTION_HELP

if TYPE_CHECKING:
    from typer.models import OptionInfo


def _make_argument_related_option(source: str | OptionInfo) -> Any:  # noqa: ANN401
    """
    Create an argument related option based on another option or create a new one.

    Args:
        source: The option to modify or param_decls of the new option.

    Returns:
        A modified option or a new option based on the source.
    """
    if isinstance(source, str):
        return typer.Option(None, source, help=LOOK_INTO_ARGUMENT_OPTION_HELP)
    return modified_param(source, default=None, help=LOOK_INTO_ARGUMENT_OPTION_HELP)


account_name = _make_argument_related_option(options.account_name)

profile_name = _make_argument_related_option(options.profile_name)

name = _make_argument_related_option("--name")

key = _make_argument_related_option("--key")

alias = _make_argument_related_option("--alias")

proposal_id = _make_argument_related_option("--proposal-id")

transaction_id = _make_argument_related_option("--transaction-id")

chain_id = _make_argument_related_option("--chain-id")

node_address = _make_argument_related_option("--node-address")
