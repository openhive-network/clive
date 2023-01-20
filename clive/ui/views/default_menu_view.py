from __future__ import annotations
from typing import List, TYPE_CHECKING

from prompt_toolkit.widgets import MenuItem
from prompt_toolkit.layout import AnyContainer

from clive.ui.component import safe_edit
from clive.ui.translation import t
from clive.ui.view_manager import ViewManager
from clive.ui.views.menu_view import MenuView

if TYPE_CHECKING:
    from clive.ui.menu_handlers import MenuHandlers


class DefaultMenuView(MenuView):
    @property
    def handlers(self) -> MenuHandlers:
        return self.__handlers

    @handlers.setter
    @safe_edit
    def handlers(self, value: MenuHandlers) -> None:
        self.__handlers = value

    def _menu_structure(self) -> List[MenuItem]:
        assert self.handlers is not None, "Handlers has not been defined"
        return [
            MenuItem(
                t("Wallet"),
                children=[
                    MenuItem(t("Dashboard"), handler=self.__handlers.dashboard),
                    MenuItem(t("Manage Accounts"), handler=self.__handlers.manage_accounts),
                    MenuItem(t("Manage Watched Accounts"), handler=self.__handlers.manage_watched_accounts),
                    MenuItem(t("Manage Private Keys"), handler=self.__handlers.manage_private_keys),
                    MenuItem(t("Exit"), handler=self.__handlers.exit),
                ],
            ),
            MenuItem(
                t("Operation"),
                children=[
                    MenuItem(
                        t("Transfer"),
                        children=[
                            MenuItem(
                                t("HIVE"),
                                children=[
                                    MenuItem(t("to Account"), handler=self.__handlers.transfer_hive_to_account),
                                    MenuItem(t("to Savings"), handler=self.__handlers.transfer_hive_to_savings),
                                    MenuItem(t("from Savings"), handler=self.__handlers.transfer_hive_from_savings),
                                ],
                            ),
                            MenuItem(
                                t("HBD"),
                                children=[
                                    MenuItem(t("to Account"), handler=self.__handlers.transfer_hbd_to_account),
                                    MenuItem(t("to Savings"), handler=self.__handlers.transfer_hbd_to_savings),
                                    MenuItem(t("from Savings"), handler=self.__handlers.transfer_hbd_from_savings),
                                ],
                            ),
                        ],
                    ),
                    MenuItem(
                        t("Vote"),
                        children=[
                            MenuItem(t("for Proposal"), handler=self.__handlers.vote_for_proposal),
                            MenuItem(t("for Witness"), handler=self.__handlers.vote_for_witness),
                            MenuItem(
                                t("for Witness as Delegatee"), handler=self.__handlers.vote_for_witness_as_delegatee
                            ),
                        ],
                    ),
                    MenuItem(
                        t("Witness"),
                        children=[
                            MenuItem(t("Update Witness Properties"), handler=self.__handlers.update_witness_properties)
                        ],
                    ),
                    MenuItem(
                        t("Convert"),
                        children=[
                            MenuItem(t("HIVE to HBD"), handler=self.__handlers.convert_hive_to_hbd),
                            MenuItem(t("HD to HIVE"), handler=self.__handlers.convert_hbd_to_hive),
                        ],
                    ),
                    MenuItem(t("Power Up/Down"), handler=self.__handlers.power_up_down),
                ],
            ),
            MenuItem(
                t("Account"),
                children=[
                    MenuItem(t("History"), handler=self.__handlers.account_history),
                    MenuItem(
                        t("Update"),
                        children=[
                            MenuItem(t("Metadata"), handler=self.__handlers.account_update_metadata),
                            MenuItem(t("Authority"), handler=self.__handlers.account_update_authority),
                            MenuItem(t("Memo key"), handler=self.__handlers.account_update_memo_key),
                        ],
                    ),
                ],
            ),
            MenuItem(
                t("Options"),
                children=[
                    MenuItem(t("Set Node Address"), handler=self.__handlers.options_set_node_address),
                    MenuItem(t("Set Theme"), handler=self.__handlers.options_set_theme),
                    MenuItem(t("Set Wallet Password"), handler=self.__handlers.options_wallet_password),
                ],
            ),
            MenuItem(
                t("Help"),
                children=[
                    MenuItem(t("Help"), handler=self.__handlers.help),
                    MenuItem(t("About"), handler=self.__handlers.about),
                    MenuItem(t("Contribute"), handler=self.__handlers.contribute),
                ],
            ),
        ]
