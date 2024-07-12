from __future__ import annotations

from textual.widgets import Select
from textual.widgets._select import NoSelection, SelectType


class CliveSelect(Select[SelectType]):
    @property
    def value_ensure(self) -> SelectType:
        """
        Easier access to ensure selected value (SelectType) is returned and not SelectType | NoSelection.

        Textual's Select widget has allow_blank=False parameter, but does not provide easy access to
        tighten the type to SelectType. This property allows for that.
        """
        assert not isinstance(self.value, NoSelection), "Value is not selected"
        return self.value
