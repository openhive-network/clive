from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import TabPane

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.bindings.operation_action_bindings import OperationActionBindings
from clive.__private.ui.widgets.generous_button import GenerousButton
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.hive_asset_amount_input import HiveAssetAmountInput
from clive.__private.ui.widgets.notice import Notice
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import Section
from schemas.operations import TransferToVestingOperation as TransferToVesting

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult

    from clive.models import Asset


class PowerUp(TabPane, OperationActionBindings):
    """TabPane with all content about power up."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType) -> None:
        """
        Initialize a TabPane.

        Args:
        ----
        title: Title of the TabPane (will be displayed in a tab label).
        """
        super().__init__(title=title)
        self._receiver_input = AccountNameInput("Receiver", value=self.working_account)
        self._asset_input = HiveAssetAmountInput()

    def compose(self) -> ComposeResult:
        with ScrollablePart():
            yield Notice("Your governance voting power will be increased after 30 days")
            with Section("Perform a power up (transfer to vesting)"):
                yield self._receiver_input
                with Horizontal(id="input-with-button"):
                    yield self._asset_input
                    yield GenerousButton(self._asset_input, self._get_hive_balance)  # type: ignore[arg-type]

    def _get_hive_balance(self) -> Asset.Hive:
        return self.profile_data.working_account.data.hive_balance

    def _create_operation(self) -> TransferToVesting | None:
        if not CliveValidatedInput.validate_many(self._asset_input, self._receiver_input):
            return None

        return TransferToVesting(
            from_=self.working_account, to=self._receiver_input.value_or_error, amount=self._asset_input.value_or_error
        )

    @property
    def working_account(self) -> str:
        return self.profile_data.working_account.name
