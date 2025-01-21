from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from clive.__private.ui.data_providers.abc.data_provider import DataProvider


class APR(DynamicLabel, AbstractClassMessagePump):
    DEFAULT_CSS = """
    APR {
        height: 1;
        margin-top: 1;
        background: $primary-darken-3;
        text-style: bold;
        align: center middle;
        width: 1fr;
    }
    """

    def __init__(self, provider: DataProvider[Any]) -> None:
        super().__init__(
            obj_to_watch=provider,
            attribute_name="_content",
            callback=self._get_apr,
            first_try_callback=lambda content: content is not None,
        )
        self._provider = provider

    @abstractmethod
    def _get_apr(self, content: Any) -> str:  # noqa: ANN401
        """Return text for displaying in apr label."""
