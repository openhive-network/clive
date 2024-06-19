from __future__ import annotations

from inspect import isawaitable
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar, cast, overload

from textual.widgets import Label

from clive.__private.core.callback import count_parameters
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult
    from textual.reactive import Reactable


T = TypeVar("T")

WatchLikeCallbackBothValuesType = Callable[[Any, Any], Awaitable[T]] | Callable[[Any, Any], T]
WatchLikeCallbackNewValueType = Callable[[Any], Awaitable[T]] | Callable[[Any], T]
WatchLikeCallbackNoArgsType = Callable[[], Awaitable[T]] | Callable[[], T]

WatchLikeCallbackType = (
    WatchLikeCallbackBothValuesType[T] | WatchLikeCallbackNewValueType[T] | WatchLikeCallbackNoArgsType[T]
)

DynamicLabelCallbackType = WatchLikeCallbackType[str]
DynamicLabelFirstTryCallbackType = WatchLikeCallbackType[bool]


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

    @overload
    def _call_with_arbitrary_args(
        self,
        callback: DynamicLabelCallbackType,
        old_value: Any,  # noqa: ANN401
        value: Any,  # noqa: ANN401
    ) -> Awaitable[str] | str: ...

    @overload
    def _call_with_arbitrary_args(
        self,
        callback: DynamicLabelFirstTryCallbackType,
        old_value: Any,  # noqa: ANN401
        value: Any,  # noqa: ANN401
    ) -> Awaitable[bool] | bool: ...

    def _call_with_arbitrary_args(
        self,
        callback: DynamicLabelCallbackType | DynamicLabelFirstTryCallbackType,
        old_value: Any,
        value: Any,
    ) -> Awaitable[str] | str | Awaitable[bool] | bool:
        param_count = count_parameters(callback)

        if param_count == 2:  # noqa: PLR2004
            return cast(WatchLikeCallbackBothValuesType[Any], callback)(old_value, value)
        if param_count == 1:
            return cast(WatchLikeCallbackNewValueType[Any], callback)(old_value)

        return cast(WatchLikeCallbackNoArgsType[Any], callback)()
