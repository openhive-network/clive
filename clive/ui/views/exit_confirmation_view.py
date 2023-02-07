from __future__ import annotations

from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Label

from clive.get_clive import get_clive
from clive.ui.view import View


class ExitConfirmationView(View):
    def _create_container(self) -> AnyContainer:
        get_clive().exit()
        return Label("Never reached")
