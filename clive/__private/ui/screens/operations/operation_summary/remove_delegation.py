from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.constants.node import VESTS_TO_REMOVE_DELEGATION
from clive.__private.models import Asset
from clive.__private.models.schemas import DelegateVestingSharesOperation
from clive.__private.ui.screens.operations.operation_summary.operation_summary import OperationSummary
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.models.schemas import VestingDelegation


class RemoveDelegation(OperationSummary):
    """Screen to remove delegation."""

    SECTION_TITLE: ClassVar[str] = "Remove delegation"

    def __init__(self, delegation: VestingDelegation, pretty_hp_amount: str) -> None:
        super().__init__()
        self._delegation = delegation
        self._pretty_hp_amount = pretty_hp_amount

    @property
    def working_account_name(self) -> str:
        return self.profile.accounts.working.name

    def content(self) -> ComposeResult:
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
            vesting_shares=Asset.vests(VESTS_TO_REMOVE_DELEGATION),
        )
