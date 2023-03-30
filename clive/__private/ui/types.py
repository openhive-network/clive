from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from textual.binding import Binding
    from textual.dom import DOMNode

    NamespaceBindingsMapType: TypeAlias = dict[str, tuple[DOMNode, Binding]]
