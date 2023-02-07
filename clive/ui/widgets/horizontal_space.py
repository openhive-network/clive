from __future__ import annotations

from prompt_toolkit.layout import AnyDimension, Window


class HorizontalSpace(Window):
    """An empty horizontal space"""

    def __init__(self, height: AnyDimension = 1) -> None:
        super().__init__(height=height, char="")
