from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Container, Horizontal
from textual.widgets import Button, TabPane

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.governance_operations.common_governance.governance_tab_pane import ScrollablePart
from clive.__private.ui.operations.raw.account_witness_proxy.account_witness_proxy import AccountWitnessProxy
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.ui.widgets.notice import Notice

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class ProxyBaseContainer(Container):
    """Base widget for the ProxyNotSet and ProxySet container to properly catch both by the query_one."""


class ProxyInput(AccountNameInput):
    pass


class ProxyNotSet(ProxyBaseContainer):
    def compose(self) -> ComposeResult:
        yield AccountNameInput(label="current proxy", value="Not set", disabled=True)
        yield ProxyInput()
        with Container(id="set-button-container"):
            yield CliveButton("Set proxy", id_="set-proxy-button")
        yield Notice(
            "setting proxy will delete your witnesses votes and deactivate your proposal votes",
        )


class ProxySet(ProxyBaseContainer):
    def __init__(self, current_proxy: str) -> None:
        """
        Initialize the ProxySet Container.

        Args:
        ----
        current_proxy: Proxy that is currently assigned to the account.
        """
        super().__init__()
        self._current_proxy = current_proxy

    def compose(self) -> ComposeResult:
        yield AccountNameInput(label="current proxy", value=self._current_proxy, disabled=True)
        yield ProxyInput()
        with Horizontal(id="modify-proxy-buttons"):
            yield CliveButton("Change proxy", id_="set-proxy-button")
            yield CliveButton("Remove proxy", id_="remove-proxy-button")


class Proxy(TabPane, CliveWidget):
    """TabPane with all content about proxy."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType):
        super().__init__(title=title)
        self._current_proxy = self.app.world.profile_data.working_account.data.proxy

    def on_mount(self) -> None:
        self.watch(self.app.world, "profile_data", self.sync_when_proxy_changed)

    @property
    def new_proxy(self) -> str | None:
        return self.query_one(ProxyInput).value

    def compose(self) -> ComposeResult:
        content = ProxySet(self._current_proxy) if self._current_proxy else ProxyNotSet()
        with ScrollablePart():
            yield content

    @on(Button.Pressed, "#set-proxy-button")
    def set_new_proxy(self) -> None:
        if not self.new_proxy:
            return

        working_account_name = self.app.world.profile_data.working_account.name

        if self.new_proxy == working_account_name:
            self.notify("You cannot set the proxy on yourself!", severity="error")
            return

        self.app.push_screen(AccountWitnessProxy(is_raw=False, new_proxy=self.new_proxy))

    @on(Button.Pressed, "#remove-proxy-button")
    def remove_proxy(self) -> None:
        self.app.push_screen(AccountWitnessProxy(is_raw=False))

    def sync_when_proxy_changed(self) -> None:
        proxy_profile_data = self.app.world.profile_data.working_account.data.proxy
        if self._current_proxy != proxy_profile_data:
            self._current_proxy = proxy_profile_data

            content = ProxySet(self._current_proxy) if self._current_proxy else ProxyNotSet()

            with self.app.batch_update():
                self.query_one(ProxyBaseContainer).remove()
                self.query_one(ScrollablePart).mount(content)
