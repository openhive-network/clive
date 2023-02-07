from __future__ import annotations

from clive.exceptions import FormNotFinishedExceptionError
from clive.storage.mock_database import MockDB
from clive.ui.manage_keys import ManageKeysView
from clive.ui.manage_watched_accounts import ManageWatchedAccountView
from clive.ui.set_node_address import SetNodeAddressView
from clive.ui.view_switcher import switch_view
from clive.ui.views.form import Form


class QuickSetup(Form):
    def __init__(self) -> None:
        super().__init__(
            [
                ManageKeysView.convert_to_form_view(self),
                ManageWatchedAccountView.convert_to_form_view(self),
                SetNodeAddressView.convert_to_form_view(self),
            ]
        )

    def cancel(self) -> None:
        switch_view("dashboard")

    def finish(self) -> None:
        checks = [
            MockDB.MAIN_ACTIVE_ACCOUNT is not None,
            len(MockDB.MAIN_ACTIVE_ACCOUNT.keys) > 0,
            MockDB.NODE_ADDRESS is not None,
        ]
        if not all(checks):
            raise FormNotFinishedExceptionError(
                **dict(zip(["is main account set", "is any private key set", "is any node address set"], checks))
            )
        else:
            switch_view("dashboard")
