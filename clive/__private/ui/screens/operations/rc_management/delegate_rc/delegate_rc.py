from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal
from textual.widgets import Static, TabPane

from clive.__private.core.constants.tui.class_names import CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME
from clive.__private.core.ensure_vests import ensure_vests
from clive.__private.core.wax_operation_wrapper import WaxRcDelegationWrapper
from clive.__private.models.schemas import CustomJsonOperation
from clive.__private.ui.data_providers.rc_data_provider import RcDataProvider
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.not_updated_yet import NotUpdatedYet
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
from clive.__private.ui.widgets.buttons import CliveButton, OneLineButton
from clive.__private.ui.widgets.clive_basic import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.hp_vests_amount_input import HPVestsAmountInput
from clive.__private.ui.widgets.inputs.receiver_input import ReceiverInput
from clive.__private.ui.widgets.place_taker import PlaceTaker
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import Section
from clive.__private.ui.widgets.transaction_buttons import TransactionButtons

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.rc_data import RcData
    from clive.__private.models.schemas import RcDirectDelegation


class RcDelegationsTableHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("Delegatee", classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)
        yield Static("RC \\[HP]", classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)
        yield Static("RC \\[VESTS]", classes=CLIVE_CHECKERBOARD_HEADER_CELL_CLASS_NAME)
        yield PlaceTaker()


class RcDelegationRow(CliveCheckerboardTableRow):
    def __init__(self, delegation: RcDirectDelegation, aligned_hp_amount: str, aligned_vests_amount: str) -> None:
        super().__init__(
            CliveCheckerBoardTableCell(str(delegation.to)),
            CliveCheckerBoardTableCell(aligned_hp_amount),
            CliveCheckerBoardTableCell(aligned_vests_amount),
            CliveCheckerBoardTableCell(OneLineButton("Revoke", id_="revoke-rc-delegation-button", variant="error")),
        )
        self._delegation = delegation

    @on(CliveButton.Pressed, "#revoke-rc-delegation-button")
    def revoke_delegation(self) -> None:
        wrapper = WaxRcDelegationWrapper.create_removal(
            from_account=self.profile.accounts.working.name, delegatee=str(self._delegation.to)
        )
        operation = wrapper.to_schemas(self.world.wax_interface, CustomJsonOperation)
        self.profile.transaction.add_operation(operation)
        self.notify(f"Revoke RC delegation to {self._delegation.to} added to cart.")


class RcDelegationsTable(CliveCheckerboardTable):
    ATTRIBUTE_TO_WATCH = "_content"
    NO_CONTENT_TEXT = "No outgoing RC delegations"

    def __init__(self) -> None:
        super().__init__(header=RcDelegationsTableHeader(), title="Current outgoing RC delegations", init_dynamic=False)
        self._previous_delegations: list[RcDirectDelegation] | NotUpdatedYet = NotUpdatedYet()

    def create_dynamic_rows(self, content: RcData) -> list[RcDelegationRow]:
        aligned_hp, aligned_vests = content.get_delegations_aligned_amounts()

        return [
            RcDelegationRow(delegation, hp_value, vests_value)
            for delegation, hp_value, vests_value in zip(
                content.outgoing_delegations, aligned_hp, aligned_vests, strict=True
            )
        ]

    def check_if_should_be_updated(self, content: RcData) -> bool:
        return self._previous_delegations != content.outgoing_delegations

    def is_anything_to_display(self, content: RcData) -> bool:
        return len(content.outgoing_delegations) != 0

    @property
    def object_to_watch(self) -> RcDataProvider:
        return self.screen.query_exactly_one(RcDataProvider)

    def update_previous_state(self, content: RcData) -> None:
        self._previous_delegations = content.outgoing_delegations


class DelegateRc(TabPane, OperationActionBindings):
    """TabPane with all content about delegate RC."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        super().__init__(title="Delegate RC")
        self._delegatee_input = ReceiverInput("Delegatee")
        self._rc_amount_input = HPVestsAmountInput()

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            with Section("Delegate your resource credits"):
                yield self._delegatee_input
                yield self._rc_amount_input
                yield TransactionButtons()
            yield RcDelegationsTable()

    def _create_operation(self) -> CustomJsonOperation | None:
        if not CliveValidatedInput.validate_many(self._delegatee_input, self._rc_amount_input):
            return None

        asset = self._rc_amount_input.value_or_error

        # If the user has passed an amount in `HP` - convert it to `VESTS`. RC amount is equivalent to VESTS amount.
        vests = ensure_vests(asset, self.provider.content.gdpo)
        wrapper = WaxRcDelegationWrapper.create_delegation(
            from_account=self.profile.accounts.working.name,
            delegatee=self._delegatee_input.value_or_error,
            max_rc=vests.amount,
        )
        return wrapper.to_schemas(self.world.wax_interface, CustomJsonOperation)

    @property
    def provider(self) -> RcDataProvider:
        return self.screen.query_exactly_one(RcDataProvider)
