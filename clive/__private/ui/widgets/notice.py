from __future__ import annotations

from typing import TYPE_CHECKING, Any

from clive.__private.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.reactive import Reactable


class Notice(TitledLabel):
    DEFAULT_CSS = """
    Notice {
        color: $text;
        background: $warning;
        align: center middle;
        height: 1;
        width: 1fr;
    }
    """

    def __init__(
        self,
        value: str = "",
        *,
        obj_to_watch: Reactable | None = None,
        attribute_name: str | None = None,
        callback: Callable[[Any], Any] | None = None,
        init: bool = True,
    ) -> None:
        super().__init__(
            "[bold]Notice[/bold]",
            value,
            obj_to_watch=obj_to_watch,
            attribute_name=attribute_name,
            callback=callback,
            init=init,
        )
