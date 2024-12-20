from __future__ import annotations

from typing import TYPE_CHECKING, cast

from textual.binding import Binding

if TYPE_CHECKING:
    from textual.binding import BindingType


def ensure_bindings_with_binding_type(bindings: list[BindingType]) -> list[Binding]:
    """
    Check if all bindings are instances of Binding class.

    Args:
    ----
    bindings: list of bindings to check.

    Returns:
    -------
    list[Binding]: list of bindings.

    Raises:
    ------
    AssertionError: if any binding is not an instance of Binding.
    """
    for binding in bindings:
        assert isinstance(binding, Binding), f"Binding {binding} is not an instance of Binding class!"
    return cast(list[Binding], bindings)
