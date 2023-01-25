from __future__ import annotations

from typing import TYPE_CHECKING

from clive.ui.menus.menu_handlers import MenuHandlers
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
    from clive.ui.menus.full.menu_full import MenuFull


class MenuFullHandlers(MenuHandlers["MenuFull"]):
    def __init__(self, parent: MenuFull) -> None:
        super().__init__(parent)

        self.dashboard = self._switch_view(Dashboard)
        self.manage_accounts = self._switch_view(ManageAccountsView)
        self.manage_watched_accounts = self._switch_view(ManageWatchedAccountsView)
        self.manage_private_keys = self._switch_view(ManagePrivateKeysView)
        self.exit = self._switch_view(ExitConfirmationView)

        self.transfer_hive_to_account = self._switch_view(TransferToAccountView, asset="HIVE")
        self.transfer_hive_to_savings = self._switch_view(TransferToSavingsView, asset="HIVE")
        self.transfer_hive_from_savings = self._switch_view(TransferFromSavingsView, asset="HIVE")

        self.transfer_hbd_to_account = self._switch_view(TransferToAccountView, asset="HBD")
        self.transfer_hbd_from_savings = self._switch_view(TransferFromSavingsView, asset="HBD")
        self.transfer_hbd_to_savings = self._switch_view(TransferToSavingsView, asset="HBD")

        self.vote_for_proposal = self._switch_view(VoteForProposalView)
        self.vote_for_witness = self._switch_view(VoteForWitnessView)
        self.vote_for_witness_as_delegatee = self._switch_view(VoteForWitnessAsDelegateeView)

        self.update_witness_properties = self._switch_view(UpdateWitnessPropertiesView)

        self.convert_hive_to_hbd = self._switch_view(ConvertView, source_asset="HIVE", destination_asset="HBD")
        self.convert_hbd_to_hive = self._switch_view(ConvertView, source_asset="HBD", destination_asset="HIVE")

        self.power_up_down = self._switch_view(PowerUpDownView)

        self.account_history = self._switch_view(AccountHistoryView)

        self.account_update_metadata = self._switch_view(AccountUpdateMetadataView)
        self.account_update_authority = self._switch_view(AccountUpdateAuthorityView)
        self.account_update_memo_key = self._switch_view(AccountUpdateMemoKeyView)

        self.options_set_node_address = self._switch_view(SetNodeAddressView)
        self.options_set_theme = self._switch_view(SetThemeView)
        self.options_wallet_password = self._switch_view(SetWalletPasswordView)

        self.help = self._switch_view(HelpView)
        self.about = self._switch_view(AboutView)
        self.contribute = self._switch_view(ContributeView)
