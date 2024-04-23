from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from clive.__private.ui.operations.operation_summary.operation_summary import OperationSummary
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from clive.models import Asset
from schemas.operations import DelegateVestingSharesOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models.aliased import VestingDelegation


DELEGATION_REMOVE_VESTS_VALUE: Final[Asset.Vests] = Asset.vests(0)


class RemoveDelegation(OperationSummary):
    """Screen to remove delegation."""

    SECTION_TITLE: ClassVar[str] = "Remove delegation"

    def __init__(self, delegation: VestingDelegation[Asset.Vests], pretty_hp_amount: str) -> None:
        super().__init__()
        self._delegation = delegation
        self._pretty_hp_amount = pretty_hp_amount

    def content(self) -> ComposeResult:
        yield LabelizedInput("Delegator", self.working_account)
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
            delegator=self.working_account,
            delegatee=self._delegation.delegatee,
            vesting_shares=DELEGATION_REMOVE_VESTS_VALUE,
        )

    @property
    def working_account(self) -> str:
        return self.app.world.profile_data.working_account.name
