from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

from textual.reactive import reactive
from textual.widgets import Label

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import (
    DynamicLabel,
)

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.reactive import Reactable

    from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabelCallbackType
    from clive.__private.ui.widgets.dynamic_widgets.dynamic_widget import DynamicWidgetFirstTryCallbackType

NoticeVariant = Literal["default", "grey"]


class Notice(CliveWidget):
    TITLE: Final[str] = "Notice"

    DEFAULT_CSS = """
    Notice {
        height: auto;

        Label {
            color: $text;
            width: 1fr;
            text-align: center;
            padding: 0 1;
        }

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
        shrink: bool = True,
    ) -> None:
        super().__init__()
        self._value = value
        self._obj_to_watch = obj_to_watch
        self._attribute_name = attribute_name
        self._callback = callback
        self._first_try_callback = first_try_callback
        self._init = init
        self.variant = variant
        self._shrink = shrink

    @property
    def is_dynamic(self) -> bool:
        return bool(self._obj_to_watch) and bool(self._attribute_name) and bool(self._callback)

    @property
    def titled_value(self) -> str:
        return f"[b]{self.TITLE}:[/] {self._value}"

    def compose(self) -> ComposeResult:
        if self.is_dynamic:
            assert self._obj_to_watch is not None, "Object to watch shouldn't be None, it was checked already."
            assert self._attribute_name is not None, "Attribute name shouldn't be None, it was checked already."
            assert self._callback is not None, "Callback shouldn't be None, it was checked already."

            yield DynamicLabel(
                self._obj_to_watch,
                self._attribute_name,
                self._callback,
                prefix=self.titled_value,
                first_try_callback=self._first_try_callback,
                init=self._init,
                shrink=self._shrink,
            )
        else:
            yield Label(self.titled_value, shrink=self._shrink)

    def watch_variant(self, old_variant: str, variant: str) -> None:
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")

    def force_dynamic_update(self) -> None:
        assert self.is_dynamic, "This method should be called only when the notice is dynamic."
        self.query_exactly_one(DynamicLabel).force_update()
