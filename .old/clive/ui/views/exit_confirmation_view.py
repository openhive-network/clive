from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.widgets import Label

from clive.get_clive import get_clive
from clive.ui.view import View

if TYPE_CHECKING:
    from prompt_toolkit.layout import AnyContainer


class ExitConfirmationView(View):
    def _create_container(self) -> AnyContainer:
        get_clive().exit()
        return Label("Never reached")
