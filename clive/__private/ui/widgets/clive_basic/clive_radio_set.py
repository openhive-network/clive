from __future__ import annotations

from textual.widgets import RadioSet


class CliveRadioSet(RadioSet):
    def watch__selected(self) -> None:
        """
        Refresh when the selected button changes.

        It is needed because the textual radio set is bugged, when selected radio button changed, background of previous
        one is not refreshed sometimes.
        Problem is described here: https://github.com/Textualize/textual/issues/4785#issuecomment-2242312224
        """
        super().watch__selected()
        self.refresh(layout=True)
