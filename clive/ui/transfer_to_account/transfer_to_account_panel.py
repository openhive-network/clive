from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import AnyContainer, HSplit
from prompt_toolkit.widgets import Label

from clive.ui.component import Component

if TYPE_CHECKING:
    from clive.ui.transfer_to_account.transfer_to_account_view import TransferToAccountView  # noqa: F401


class TransferToAccountPanel(Component["TransferToAccountView"]):
    def __init__(self, parent: TransferToAccountView):
        super().__init__(parent)

    def _create_container(self) -> AnyContainer:
        return HSplit(
            [
                Label(f"{self._parent.asset} transfer to account - prepare operation"),
            ]
        )
