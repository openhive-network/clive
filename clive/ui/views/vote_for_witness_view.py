from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.widgets import Label

from clive.ui.view import View

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer


class VoteForWitnessView(View):
    def _create_container(self) -> AnyContainer:
        return Label(text=self.__class__.__name__)
