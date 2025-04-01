from __future__ import annotations

from textual.widgets import Select
from textual.widgets._select import SelectType


class CliveSelect(Select[SelectType]):
    @property
    def selection_ensure(self) -> SelectType:
        """
        Easier access to ensure selected value (SelectType) is returned and not SelectType | None.

        Textual's Select widget has allow_blank=False parameter, but does not provide easy access to
        tighten the type to SelectType. This property allows for that.
        """
        selection = self.selection
        assert selection is not None, "Value is not selected"
        return selection
