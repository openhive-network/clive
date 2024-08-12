from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual.reactive import reactive

from clive.__private.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from textual.reactive import Reactable

    from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import (
        DynamicLabelCallbackType,
    )
    from clive.__private.ui.widgets.dynamic_widgets.dynamic_widget import (
        DynamicWidgetFirstTryCallbackType,
    )


NoticeVariant = Literal["default", "grey"]


class Notice(TitledLabel):
    DEFAULT_CSS = """
    Notice {
        color: $text;
        align: center middle;
        height: 1;
        width: 1fr;

        &.-default {
            background: $warning;
        }

        &.-grey {
            background: $primary-background;
        }
    }
    """
    variant: NoticeVariant = reactive("default")  # type: ignore[assignment]

    def __init__(
        self,
        value: str = "",
        *,
        obj_to_watch: Reactable | None = None,
        attribute_name: str | None = None,
        callback: DynamicLabelCallbackType | None = None,
        first_try_callback: DynamicWidgetFirstTryCallbackType = lambda: True,
        init: bool = True,
        variant: NoticeVariant = "default",
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
        self.variant = variant

    def watch_variant(self, old_variant: str, variant: str) -> None:
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")
