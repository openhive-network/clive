from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.account_managament_reference import AccountManagementReference
from clive.__private.ui.widgets.switch_working_account_container import (
    SwitchWorkingAccountContainer,
)

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SwitchWorkingAccountDialog(CliveActionDialog):
    CSS_PATH = [get_relative_css_path(__file__)]
    BINDINGS = [Binding("escape,f3", "cancel", "Cancel")]
    AUTO_FOCUS = "RadioSet"

    def __init__(self) -> None:
        super().__init__(border_title="Switch working account")
        self._switch_working_account_container = SwitchWorkingAccountContainer(show_title=False)

    def create_dialog_content(self) -> ComposeResult:
        yield AccountManagementReference()
        yield self._switch_working_account_container

    async def _perform_confirmation(self) -> bool:
        self._switch_working_account_container.confirm_selected_working_account()
        return True
