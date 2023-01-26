from clive.ui.manage_keys.manage_keys_view import ManageKeysView
from clive.ui.manage_watched_accounts.manage_watched_accounts_view import ManageWatchedAccountView
from clive.ui.views.form import Form


class QuickSetup(Form):
    def __init__(self) -> None:
        super().__init__(
            [ManageKeysView.convert_to_form_view(self), ManageWatchedAccountView.convert_to_form_view(self)]
        )
