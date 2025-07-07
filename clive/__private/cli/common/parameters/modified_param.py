from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typer.models import ArgumentInfo, OptionInfo


def modified_param(source: OptionInfo | ArgumentInfo, **kwargs: Any) -> Any:  # noqa: ANN401
    """
    Create option/argument based on another option/argument, but with some attributes modified.

    Args:
        source: The option/argument to modify.
        **kwargs: The attributes to modify.

    Returns:
        A modified option/argument based on the source with the specified attributes changed.
    """
    destination = deepcopy(source)
    for key, value in kwargs.items():
        if not hasattr(destination, key):
            raise ValueError(f"Unknown option attribute: {key}\navailable attributes: {list(source.__dict__)}")
        setattr(destination, key, value)
    return destination
