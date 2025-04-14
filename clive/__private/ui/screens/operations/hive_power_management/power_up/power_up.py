from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import TabPane

from clive.__private.models.schemas import TransferToVestingOperation
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.operations.bindings.operation_action_bindings import OperationActionBindings
from clive.__private.ui.widgets.buttons import GenerousButton
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.hive_asset_amount_input import HiveAssetAmountInput
from clive.__private.ui.widgets.inputs.receiver_input import ReceiverInput
from clive.__private.ui.widgets.notice import Notice
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import Section
from clive.__private.ui.widgets.transaction_buttons import TransactionButtons

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.models import Asset


class PowerUp(TabPane, OperationActionBindings):
    """TabPane with all content about power up."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self) -> None:
        super().__init__(title="Power up")
        self._receiver_input = ReceiverInput("Receiver", value=self.working_account_name)
        self._asset_input = HiveAssetAmountInput()

    @property
    def working_account_name(self) -> str:
        return self.profile.accounts.working.name

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield Notice("Your governance voting power will be increased after 30 days")
            with Section("Perform a power up (transfer to vesting)"):
                yield self._receiver_input
                with Horizontal(id="input-with-button"):
                    yield self._asset_input
                    yield GenerousButton(self._asset_input, self._get_hive_balance)
                yield TransactionButtons()

    def _additional_actions_after_clearing_inputs(self) -> None:
        receiver_input = self.query_exactly_one(ReceiverInput)
        receiver_input.input.value = self.profile.accounts.working.name

    def _get_hive_balance(self) -> Asset.Hive:
        return self.profile.accounts.working.data.hive_balance

    def _create_operation(self) -> TransferToVestingOperation | None:
        if not CliveValidatedInput.validate_many(self._asset_input, self._receiver_input):
            return None

        return TransferToVestingOperation(
            from_=self.working_account_name,
            to=self._receiver_input.value_or_error,
            amount=self._asset_input.value_or_error,
        )
