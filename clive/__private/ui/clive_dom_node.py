from __future__ import annotations

from typing import TYPE_CHECKING, cast

from textual.dom import DOMNode

if TYPE_CHECKING:
    from clive.__private.ui.app import Clive


class CliveDOMNode(DOMNode):
    @property
    def app(self) -> Clive:  # type: ignore[override]
        return cast("Clive", super().app)
