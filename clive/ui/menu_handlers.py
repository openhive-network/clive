from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from clive.ui.parented import Parented
from clive.ui.views.about_view import AboutView
from clive.ui.views.account_history_view import AccountHistoryView
from clive.ui.views.account_update_authority_view import AccountUpdateAuthorityView
from clive.ui.views.account_update_memo_key_view import AccountUpdateMemoKeyView
from clive.ui.views.account_update_metadata_view import AccountUpdateMetadataView
from clive.ui.views.contribute_view import ContributeView
from clive.ui.views.convert_view import ConvertView
from clive.ui.views.dashboard import Dashboard
from clive.ui.views.exit_confirmation_view import ExitConfirmationView
from clive.ui.views.help_view import HelpView
from clive.ui.views.manage_accounts_view import ManageAccountsView
from clive.ui.views.manage_private_keys_view import ManagePrivateKeysView
from clive.ui.views.manage_watched_accounts_view import ManageWatchedAccountsView
from clive.ui.views.power_up_down_view import PowerUpDownView
from clive.ui.views.set_node_address_view import SetNodeAddressView
from clive.ui.views.set_theme_view import SetThemeView
from clive.ui.views.set_wallet_password_view import SetWalletPasswordView
from clive.ui.views.transfer_from_savings_view import TransferFromSavingsView
from clive.ui.views.transfer_to_account_view import TransferToAccountView
from clive.ui.views.transfer_to_savings_view import TransferToSavingsView
from clive.ui.views.update_witness_properties_view import UpdateWitnessPropertiesView
from clive.ui.views.vote_for_proposal_view import VoteForProposalView
from clive.ui.views.vote_for_witness_as_delegatee_view import VoteForWitnessAsDelegateeView
from clive.ui.views.vote_for_witness_view import VoteForWitnessView

if TYPE_CHECKING:
    from clive.ui.menu_full import MenuFull


class MenuHandlers(Parented["MenuFull"]):
    def __init__(self, parent: MenuFull) -> None:
        super().__init__(parent)

        self.dashboard = self.__default_switch_view(Dashboard)
        self.manage_accounts = self.__default_switch_view(ManageAccountsView)
        self.manage_watched_accounts = self.__default_switch_view(ManageWatchedAccountsView)
        self.manage_private_keys = self.__default_switch_view(ManagePrivateKeysView)
        self.exit = self.__default_switch_view(ExitConfirmationView)

        self.transfer_hive_to_account = self.__default_switch_view(TransferToAccountView, asset="HIVE")
        self.transfer_hive_to_savings = self.__default_switch_view(TransferToSavingsView, asset="HIVE")
        self.transfer_hive_from_savings = self.__default_switch_view(TransferFromSavingsView, asset="HIVE")

        self.transfer_hbd_to_account = self.__default_switch_view(TransferToAccountView, asset="HBD")
        self.transfer_hbd_from_savings = self.__default_switch_view(TransferFromSavingsView, asset="HBD")
        self.transfer_hbd_to_savings = self.__default_switch_view(TransferToSavingsView, asset="HBD")

        self.vote_for_proposal = self.__default_switch_view(VoteForProposalView)
        self.vote_for_witness = self.__default_switch_view(VoteForWitnessView)
        self.vote_for_witness_as_delegatee = self.__default_switch_view(VoteForWitnessAsDelegateeView)

        self.update_witness_properties = self.__default_switch_view(UpdateWitnessPropertiesView)

        self.convert_hive_to_hbd = self.__default_switch_view(ConvertView, source_asset="HIVE", destination_asset="HBD")
        self.convert_hbd_to_hive = self.__default_switch_view(ConvertView, source_asset="HBD", destination_asset="HIVE")

        self.power_up_down = self.__default_switch_view(PowerUpDownView)

        self.account_history = self.__default_switch_view(AccountHistoryView)

        self.account_update_metadata = self.__default_switch_view(AccountUpdateMetadataView)
        self.account_update_authority = self.__default_switch_view(AccountUpdateAuthorityView)
        self.account_update_memo_key = self.__default_switch_view(AccountUpdateMemoKeyView)

        self.options_set_node_address = self.__default_switch_view(SetNodeAddressView)
        self.options_set_theme = self.__default_switch_view(SetThemeView)
        self.options_wallet_password = self.__default_switch_view(SetWalletPasswordView)

        self.help = self.__default_switch_view(HelpView)
        self.about = self.__default_switch_view(AboutView)
        self.contribute = self.__default_switch_view(ContributeView)

    def __default_switch_view(self, target_view: type, **kwargs: Any) -> Callable[[], None]:
        def default_switch_view_impl() -> None:
            from clive.ui.view_switcher import switch_view

            if self.__ask_about_loosing_changes():
                switch_view(target_view(**kwargs))

        return default_switch_view_impl

    def __ask_about_loosing_changes(self) -> bool:
        """This method should check is there some unsaved progress and
            if so it should ask user about continuation

            TODO: Implement this function

        Returns:
            bool: True if switching can be continued, False otherwise
        """
        return True
