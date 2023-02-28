from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import ListView

if TYPE_CHECKING:
    from clive.ui.widgets.select.select_list import _SelectList


class _SelectListView(ListView):
    """The ListView inside the SelectList which closes the list on blur."""

    def __init__(self, select_list: _SelectList) -> None:
        super().__init__(initial_index=-1)
        self.__select_list = select_list

    def on_blur(self) -> None:
        self.__select_list.display = False
