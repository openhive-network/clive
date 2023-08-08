from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Static, TabbedContent

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.raw.account_witness_proxy.account_witness_proxy import AccountWitnessProxy
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ProxyPresent(Container):
    """Container which is displaying when account has proxy set."""

    def __init__(self, proxy: str):
        self.__proxy = proxy
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(f"Current proxy for account: {self.__proxy}", id="current-proxy")
        with Horizontal(id="delete-proxy-container"):
            yield Static("", classes="empty")
            yield Static("Delete current proxy", classes="action-proxy-label")
            yield CliveButton("Delete", id_="delete-proxy-button")
            yield Static("", classes="empty")

    @on(CliveButton.Pressed)
    def push_proxy_operation_delete_screen(self, event: CliveButton.Pressed) -> None:
        if event.button.id == "delete-proxy-button":
            self.app.push_screen(AccountWitnessProxy(delete_proxy=True))


class ProxyAbsent(Container):
    """Container which is displaying when account has not proxy set."""

    def compose(self) -> ComposeResult:
        with Horizontal(id="set-proxy-container"):
            yield Static("", classes="empty")
            yield Static("Click to set proxy for your account", classes="action-proxy-label")
            yield CliveButton("Set proxy", id_="set-proxy-button")
            yield Static("", classes="empty")
        yield Static("Notice: after setting proxy your votes for witnesses would be deleted!", id="proxy-warning")

    @on(CliveButton.Pressed)
    def push_proxy_operation_set_screen(self, event: CliveButton.Pressed) -> None:
        if event.button.id == "set-proxy-button":
            self.app.push_screen(AccountWitnessProxy())


class ProxyTab(ScrollableTabPane, CliveWidget):
    """Tab with all activities related with proxy."""

    def compose(self) -> ComposeResult:
        yield Static(
            "You cannot have set proxy and vote for witnesses/proposals at the same time",
            id="proxy-vote-information",
        )
        if proxy := self.app.world.profile_data.working_account.data.proxy:
            yield ProxyPresent(proxy=proxy)
        else:
            yield ProxyAbsent()


class WitnessesTab(ScrollableTabPane):
    """Tab with all activities related with witnesses."""


class ProposalsTab(ScrollableTabPane):
    """Tab with all activities related with witnesses."""


class Governance(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
    ]

    def create_left_panel(self) -> ComposeResult:
        with TabbedContent():
            yield ProxyTab("Proxy")
            yield WitnessesTab("Witnesses")
            yield ProposalsTab("Proposals")
