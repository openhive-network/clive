from __future__ import annotations

from prompt_toolkit.layout import AnyDimension, Window


class VerticalSpace(Window):
    """An empty vertical space."""

    def __init__(self, width: AnyDimension = 1) -> None:
        super().__init__(width=width, char="")
