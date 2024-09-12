from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

import typer

from clive.__private.core.constants.cli import LOOK_INTO_ARGUMENT_OPTION_HELP

if TYPE_CHECKING:
    from typer.models import ArgumentInfo, OptionInfo


def modified_param(source: OptionInfo | ArgumentInfo, **kwargs: Any) -> Any:  # noqa: ANN401
    """
    Create option/argument based on another option/argument, but with some attributes modified.

    Args:
    ----
    source: The option/argument to modify.
    kwargs: The attributes to modify.
    """
    destination = deepcopy(source)
    for key, value in kwargs.items():
        if not hasattr(destination, key):
            raise ValueError(f"Unknown option attribute: {key}\navailable attributes: {list(source.__dict__)}")
        setattr(destination, key, value)
    return destination


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
