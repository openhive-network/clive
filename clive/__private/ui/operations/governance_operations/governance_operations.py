from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.operations.governance_operations.governance_data import GovernanceDataProvider
from clive.__private.ui.operations.governance_operations.witness import Witnesses
from textual import on
from textual.containers import Container, Horizontal
from textual.widgets import Button, Static

from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from clive.__private.ui.widgets.clive_tabbed_content import CliveTabbedContent
from clive.__private.ui.operations.raw.account_witness_proxy.account_witness_proxy import AccountWitnessProxy
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class Proxy(ScrollableTabPane, CliveWidget):
    """TabPane with all content about proxy."""

    def __init__(self, title: TextType):
        super().__init__(title=title)
        self.__proxy_input = AccountNameInput()
        self.__current_proxy = self.app.world.profile_data.working_account.data.proxy

    @property
    def new_proxy(self) -> str | None:
        return self.__proxy_input.value

    def compose(self) -> ComposeResult:
        content = self.__compose_proxy_set if self.__current_proxy else self.__compose_proxy_not_set
        yield from content()

    def __compose_proxy_not_set(self) -> ComposeResult:
        yield AccountNameInput(label="current proxy", value="Not set", disabled=True)
        yield self.__proxy_input
        with Container(id="set-button-container"):
            yield CliveButton("Set proxy", id_="set-proxy-button")
        yield Static(
            "Notice: setting proxy will delete your witnesses votes and deactivate your proposal votes",
            id="proxy-set-information",
        )

    def __compose_proxy_set(self) -> ComposeResult:
        yield AccountNameInput(label="current proxy", value=self.__current_proxy, disabled=True)
        yield self.__proxy_input
        with Horizontal(id="modify-proxy-buttons"):
            yield CliveButton("Change proxy", id_="set-proxy-button")
            yield CliveButton("Remove proxy", id_="remove-proxy-button")

    @on(Button.Pressed, "#set-proxy-button")
    def set_new_proxy(self) -> None:
        if not self.new_proxy:
            return

        self.app.push_screen(AccountWitnessProxy(is_raw=False, new_proxy=self.new_proxy))

    @on(Button.Pressed, "#remove-proxy-button")
    def remove_proxy(self) -> None:
        self.app.push_screen(AccountWitnessProxy(is_raw=False))


class Proposals(ScrollableTabPane):
    """TabPane with all content about proposals."""


class Governance(OperationBaseScreen):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def create_left_panel(self) -> ComposeResult:
        with GovernanceDataProvider(), CliveTabbedContent():
            yield Proxy("Proxy")
            yield Witnesses("Witnesses")
            yield Proposals("Proposals")
