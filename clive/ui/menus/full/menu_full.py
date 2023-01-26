from __future__ import annotations

from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import MenuItem

from clive.ui.menus.full.menu_full_handlers import MenuFullHandlers
from clive.ui.menus.menu import Menu


class MenuFull(Menu[MenuFullHandlers]):
    def __init__(self, body: AnyContainer) -> None:
        super().__init__(body, MenuFullHandlers(self))

    def _create_menu(self) -> list[MenuItem]:
        return [
            MenuItem(
                "Wallet",
                children=[
                    MenuItem("Dashboard", handler=self._handlers.dashboard),
                    MenuItem("Manage Private Keys", handler=self._handlers.manage_private_keys),
                    MenuItem("Manage Watched Accounts", handler=self._handlers.manage_watched_accounts),
                    MenuItem("Log out", handler=self._handlers.logout),
                    MenuItem("Exit", handler=self._handlers.exit),
                ],
            ),
            MenuItem(
                "Operation",
                children=[
                    MenuItem(
                        "Transfer",
                        children=[
                            MenuItem(
                                "HIVE",
                                children=[
                                    MenuItem("to Account", handler=self._handlers.transfer_hive_to_account),
                                    MenuItem("to Savings", handler=self._handlers.transfer_hive_to_savings),
                                    MenuItem("from Savings", handler=self._handlers.transfer_hive_from_savings),
                                ],
                            ),
                            MenuItem(
                                "HBD",
                                children=[
                                    MenuItem("to Account", handler=self._handlers.transfer_hbd_to_account),
                                    MenuItem("to Savings", handler=self._handlers.transfer_hbd_to_savings),
                                    MenuItem("from Savings", handler=self._handlers.transfer_hbd_from_savings),
                                ],
                            ),
                        ],
                    ),
                    MenuItem(
                        "Vote",
                        children=[
                            MenuItem("for Proposal", handler=self._handlers.vote_for_proposal),
                            MenuItem("for Witness", handler=self._handlers.vote_for_witness),
                            MenuItem("for Witness as Delegatee", handler=self._handlers.vote_for_witness_as_delegatee),
                        ],
                    ),
                    MenuItem(
                        "Witness",
                        children=[
                            MenuItem("Update Witness Properties", handler=self._handlers.update_witness_properties)
                        ],
                    ),
                    MenuItem(
                        "Convert",
                        children=[
                            MenuItem("HIVE to HBD", handler=self._handlers.convert_hive_to_hbd),
                            MenuItem("HD to HIVE", handler=self._handlers.convert_hbd_to_hive),
                        ],
                    ),
                    MenuItem("Power Up/Down", handler=self._handlers.power_up_down),
                ],
            ),
            MenuItem(
                "Account",
                children=[
                    MenuItem("History", handler=self._handlers.account_history),
                    MenuItem(
                        "Update",
                        children=[
                            MenuItem("Metadata", handler=self._handlers.account_update_metadata),
                            MenuItem("Authority", handler=self._handlers.account_update_authority),
                            MenuItem("Memo key", handler=self._handlers.account_update_memo_key),
                        ],
                    ),
                ],
            ),
            MenuItem(
                "Options",
                children=[
                    MenuItem("Set Node Address", handler=self._handlers.options_set_node_address),
                    MenuItem("Set Theme", handler=self._handlers.options_set_theme),
                    MenuItem("Set Wallet Password", handler=self._handlers.options_wallet_password),
                ],
            ),
            MenuItem(
                "Help",
                children=[
                    MenuItem("Help", handler=self._handlers.help),
                    MenuItem("About", handler=self._handlers.about),
                    MenuItem("Contribute", handler=self._handlers.contribute),
                ],
            ),
        ]
