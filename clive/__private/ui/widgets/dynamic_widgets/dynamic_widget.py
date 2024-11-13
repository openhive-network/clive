from __future__ import annotations

from abc import abstractmethod
from inspect import isawaitable
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generic, TypeVar, cast, overload

from textual.widget import Widget

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core.callback import count_parameters
from clive.__private.ui.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.reactive import Reactable

CallbackReturnT = TypeVar("CallbackReturnT")

WatchLikeCallbackBothValuesType = (
    Callable[[Any, Any], Awaitable[CallbackReturnT]] | Callable[[Any, Any], CallbackReturnT]
)
WatchLikeCallbackNewValueType = Callable[[Any], Awaitable[CallbackReturnT]] | Callable[[Any], CallbackReturnT]
WatchLikeCallbackNoArgsType = Callable[[], Awaitable[CallbackReturnT]] | Callable[[], CallbackReturnT]

WatchLikeCallbackType = (
    WatchLikeCallbackBothValuesType[CallbackReturnT]
    | WatchLikeCallbackNewValueType[CallbackReturnT]
    | WatchLikeCallbackNoArgsType[CallbackReturnT]
)

DynamicWidgetCallbackType = WatchLikeCallbackType[CallbackReturnT]
DynamicWidgetFirstTryCallbackType = WatchLikeCallbackType[bool]


WidgetT = TypeVar("WidgetT", bound=Widget)


class DynamicWidget(CliveWidget, AbstractClassMessagePump, Generic[WidgetT, CallbackReturnT]):
    """A widget that can be updated dynamically when a reactive variable changes."""

    DEFAULT_CSS = """
    DynamicWidget {
        height: auto;
        width: auto;
    }
    """

    def __init__(
        self,
        obj_to_watch: Reactable,
        attribute_name: str,
        callback: DynamicWidgetCallbackType[CallbackReturnT],
        *,
        first_try_callback: DynamicWidgetFirstTryCallbackType = lambda: True,
        init: bool = True,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id_, classes=classes)

        self._widget = self._create_widget()

        self._init = init
        self._obj_to_watch = obj_to_watch
        self._attribute_name = attribute_name
        self._callback = callback
        self._first_try_callback = first_try_callback

    def compose(self) -> ComposeResult:
        yield self._widget

    def on_mount(self) -> None:
        def delegate_work(old_value: Any, value: Any) -> None:  # noqa: ANN401
            self.run_worker(self._attribute_changed(old_value, value))

        self.watch(self._obj_to_watch, self._attribute_name, delegate_work, self._init)

    @abstractmethod
    def _create_widget(self) -> WidgetT:
        """Create a widget that will be updated when the reactive variable changes."""

    @abstractmethod
    def _update_widget_state(self, result: CallbackReturnT) -> None:
        """Define how the widget should be updated with the given result."""

    async def _attribute_changed(self, old_value: Any, value: Any) -> None:  # noqa: ANN401
        callback = self._callback

        should_update = self._call_with_arbitrary_args(self._first_try_callback, old_value, value)
        if not should_update:
            return

        result = self._call_with_arbitrary_args(callback, old_value, value)
        if isawaitable(result):
            result_ = await result
        else:
            result_ = result

        self._update_widget_state(result_)

    @overload
    def _call_with_arbitrary_args(
        self,
        callback: DynamicWidgetCallbackType[CallbackReturnT],
        old_value: Any,  # noqa: ANN401
        value: Any,  # noqa: ANN401
    ) -> Awaitable[Any] | Any: ...  # noqa: ANN401

    @overload
    def _call_with_arbitrary_args(
        self,
        callback: DynamicWidgetFirstTryCallbackType,
        old_value: Any,  # noqa: ANN401
        value: Any,  # noqa: ANN401
    ) -> Awaitable[bool] | bool: ...

    def _call_with_arbitrary_args(
        self,
        callback: DynamicWidgetCallbackType[CallbackReturnT] | DynamicWidgetFirstTryCallbackType,
        old_value: Any,
        value: Any,
    ) -> Awaitable[str] | str | Awaitable[bool] | bool:
        param_count = count_parameters(callback)

        if param_count == 2:  # noqa: PLR2004
            return cast(WatchLikeCallbackBothValuesType[Any], callback)(old_value, value)
        if param_count == 1:
            return cast(WatchLikeCallbackNewValueType[Any], callback)(value)

        return cast(WatchLikeCallbackNoArgsType[Any], callback)()
