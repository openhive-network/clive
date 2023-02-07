from __future__ import annotations

from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Label

from clive.ui.view import View


class SetWalletPasswordView(View):
    def _create_container(self) -> AnyContainer:
        return Label(text=self.__class__.__name__)
