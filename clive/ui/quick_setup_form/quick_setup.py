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
        switch_view("dashboard")
