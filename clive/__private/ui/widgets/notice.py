from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from textual.reactive import Reactable

    from clive.__private.ui.widgets.dynamic_label import DynamicLabelCallbackType, FirstTryCallbackType


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
        callback: DynamicLabelCallbackType | None = None,
        first_try_callback: FirstTryCallbackType = lambda: True,
        init: bool = True,
    ) -> None:
        super().__init__(
            "[bold]Notice[/bold]",
            value,
            obj_to_watch=obj_to_watch,
            attribute_name=attribute_name,
            callback=callback,
            first_try_callback=first_try_callback,
            init=init,
        )
