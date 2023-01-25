from __future__ import annotations

from prompt_toolkit.layout import AnyContainer
from prompt_toolkit.widgets import Label, MenuContainer, MenuItem

from clive.ui.containerable import Containerable
from clive.ui.menu_handlers import MenuHandlers


class Menu(Containerable):
    def __init__(self, body: AnyContainer) -> None:
        self.__body = body or Label("Body was not set.")
        self.__handlers = MenuHandlers(self)
        self.__hidden = False
        super().__init__()

    @property
    def body(self) -> AnyContainer:
        return self.__body

    @body.setter
    def body(self, value: AnyContainer) -> None:
        self.__body = value
        self._container = self._create_container()

    @property
    def hidden(self) -> bool:
        return self.__hidden

    @hidden.setter
    def hidden(self, value: bool) -> None:
        self.__hidden = value

    def _create_container(self) -> MenuContainer:
        return MenuContainer(body=self.body, menu_items=self._create_menu())

    def _create_menu(self) -> list[MenuItem]:
        return [
            MenuItem(
                "Wallet",
                children=[
                    MenuItem("Dashboard", handler=self.__handlers.dashboard),
                    MenuItem("Manage Accounts", handler=self.__handlers.manage_accounts),
                    MenuItem("Manage Watched Accounts", handler=self.__handlers.manage_watched_accounts),
                    MenuItem("Manage Private Keys", handler=self.__handlers.manage_private_keys),
                    MenuItem("Exit", handler=self.__handlers.exit),
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
                                    MenuItem("to Account", handler=self.__handlers.transfer_hive_to_account),
                                    MenuItem("to Savings", handler=self.__handlers.transfer_hive_to_savings),
                                    MenuItem("from Savings", handler=self.__handlers.transfer_hive_from_savings),
                                ],
                            ),
                            MenuItem(
                                "HBD",
                                children=[
                                    MenuItem("to Account", handler=self.__handlers.transfer_hbd_to_account),
                                    MenuItem("to Savings", handler=self.__handlers.transfer_hbd_to_savings),
                                    MenuItem("from Savings", handler=self.__handlers.transfer_hbd_from_savings),
                                ],
                            ),
                        ],
                    ),
                    MenuItem(
                        "Vote",
                        children=[
                            MenuItem("for Proposal", handler=self.__handlers.vote_for_proposal),
                            MenuItem("for Witness", handler=self.__handlers.vote_for_witness),
                            MenuItem("for Witness as Delegatee", handler=self.__handlers.vote_for_witness_as_delegatee),
                        ],
                    ),
                    MenuItem(
                        "Witness",
                        children=[
                            MenuItem("Update Witness Properties", handler=self.__handlers.update_witness_properties)
                        ],
                    ),
                    MenuItem(
                        "Convert",
                        children=[
                            MenuItem("HIVE to HBD", handler=self.__handlers.convert_hive_to_hbd),
                            MenuItem("HD to HIVE", handler=self.__handlers.convert_hbd_to_hive),
                        ],
                    ),
                    MenuItem("Power Up/Down", handler=self.__handlers.power_up_down),
                ],
            ),
            MenuItem(
                "Account",
                children=[
                    MenuItem("History", handler=self.__handlers.account_history),
                    MenuItem(
                        "Update",
                        children=[
                            MenuItem("Metadata", handler=self.__handlers.account_update_metadata),
                            MenuItem("Authority", handler=self.__handlers.account_update_authority),
                            MenuItem("Memo key", handler=self.__handlers.account_update_memo_key),
                        ],
                    ),
                ],
            ),
            MenuItem(
                "Options",
                children=[
                    MenuItem("Set Node Address", handler=self.__handlers.options_set_node_address),
                    MenuItem("Set Theme", handler=self.__handlers.options_set_theme),
                    MenuItem("Set Wallet Password", handler=self.__handlers.options_wallet_password),
                ],
            ),
            MenuItem(
                "Help",
                children=[
                    MenuItem("Help", handler=self.__handlers.help),
                    MenuItem("About", handler=self.__handlers.about),
                    MenuItem("Contribute", handler=self.__handlers.contribute),
                ],
            ),
        ]
