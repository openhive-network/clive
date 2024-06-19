from __future__ import annotations

from inspect import isawaitable
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Union

from textual.widgets import Label

from clive.__private.core.callback import count_parameters
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult
    from textual.reactive import Reactable


DynamicLabelCallbackType = Union[
    Callable[[], Awaitable[str]],
    Callable[[Any], Awaitable[str]],
    Callable[[Any, Any], Awaitable[str]],
    Callable[[], str],
    Callable[[Any], str],
    Callable[[Any, Any], str],
]

DynamicLabelFirstTryCallbackType = Union[
    Callable[[], Awaitable[str]],
    Callable[[Any], Awaitable[str]],
    Callable[[Any, Any], Awaitable[str]],
    Callable[[], bool],
    Callable[[Any], bool],
    Callable[[Any, Any], bool],
]


class DynamicLabel(CliveWidget):
    """A label that can be updated dynamically when a reactive variable changes."""

    DEFAULT_CSS = """
    DynamicLabel {
        height: auto;
        width: auto;
    }

    DynamicLabel LoadingIndicator {
        min-height: 1;
        min-width: 5;
    }
    """

    def __init__(
        self,
        obj_to_watch: Reactable,
        attribute_name: str,
        callback: DynamicLabelCallbackType,
        *,
        first_try_callback: DynamicLabelFirstTryCallbackType = lambda: True,
        prefix: str = "",
        init: bool = True,
        shrink: bool = False,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id_, classes=classes)

        self.__label = Label("loading...", shrink=shrink)

        self._init = init
        self.__obj_to_watch = obj_to_watch
        self.__attribute_name = attribute_name
        self.__callback = callback
        self._first_try_callback = first_try_callback
        self.__prefix = prefix

    @property
    def renderable(self) -> RenderableType:
        return self.__label.renderable

    def on_mount(self) -> None:
        def delegate_work(old_value: Any, value: Any) -> None:  # noqa: ANN401
            self.run_worker(self.attribute_changed(old_value, value))

        self.watch(self.__obj_to_watch, self.__attribute_name, delegate_work, self._init)

    def compose(self) -> ComposeResult:
        yield self.__label

    async def attribute_changed(self, old_value: Any, value: Any) -> None:  # noqa: ANN401
        callback = self.__callback

        should_update = self._call_with_arbitrary_args(self._first_try_callback, old_value, value)
        if not should_update:
            return

        result = self._call_with_arbitrary_args(callback, old_value, value)
        if isawaitable(result):
            result = await result
        if result != self.__label.renderable:
            self.__label.update(f"{self.__prefix}{result}")

    def _call_with_arbitrary_args(
        self,
        callback: DynamicLabelCallbackType | DynamicLabelFirstTryCallbackType,
        old_value: Any,  # noqa: ANN401
        value: Any,  # noqa: ANN401
    ) -> Awaitable[str] | str | bool:
        param_count = count_parameters(callback)

        if param_count == 2:  # noqa: PLR2004
            return callback(old_value, value)  # type: ignore[call-arg]
        if param_count == 1:
            return callback(old_value)  # type: ignore[call-arg]

        return callback()  # type: ignore[call-arg]
