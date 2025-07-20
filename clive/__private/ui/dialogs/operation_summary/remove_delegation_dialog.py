from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.node_special_assets import DELEGATION_REMOVE_ASSETS
from clive.__private.models import Asset
from clive.__private.models.schemas import DelegateVestingSharesOperation
from clive.__private.ui.dialogs.operation_summary.operation_summary_base_dialog import OperationSummaryBaseDialog
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.models.schemas import VestingDelegation


class RemoveDelegationDialog(OperationSummaryBaseDialog):
    """
    Dialog to remove delegation.

    Args:
        delegation: The delegation to be removed.
        pretty_hp_amount: The formatted amount of HP being removed.
    """

    def __init__(self, delegation: VestingDelegation[Asset.Vests], pretty_hp_amount: str) -> None:
        super().__init__("Remove delegation")
        self._delegation = delegation
        self._pretty_hp_amount = pretty_hp_amount

    @property
    def working_account_name(self) -> str:
        return self.profile.accounts.working.name

    def create_dialog_content(self) -> ComposeResult:
        yield LabelizedInput("Delegator", self.working_account_name)
        yield LabelizedInput("Delegate", self._delegation.delegatee)
        yield LabelizedInput(
            "Shares [HP]",
            self._pretty_hp_amount,
        )
        yield LabelizedInput(
            "Shares [VESTS]",
            f"{Asset.pretty_amount(self._delegation.vesting_shares)}",
        )

    def _create_operation(self) -> DelegateVestingSharesOperation:
        return DelegateVestingSharesOperation(
            delegator=self.working_account_name,
            delegatee=self._delegation.delegatee,
            vesting_shares=DELEGATION_REMOVE_ASSETS[1].copy(),
        )
