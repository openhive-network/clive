from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Container, Horizontal
from textual.widgets import Button, TabPane

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.operation_summary.account_witness_proxy import AccountWitnessProxy
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from clive.__private.ui.widgets.inputs.proxy_input import ProxyInput
from clive.__private.ui.widgets.notice import Notice
from clive.__private.ui.widgets.scrolling import ScrollablePart
from clive.__private.ui.widgets.section import SectionScrollable

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class ProxyBaseContainer(Container):
    """Base widget for the ProxyNotSet and ProxySet container to properly catch both by the query_one."""


class CurrentProxy(LabelizedInput):
    def __init__(self, current_proxy: str) -> None:
        super().__init__("Current proxy", current_proxy)


class NewProxyInput(ProxyInput):
    def __init__(self, required: bool) -> None:
        super().__init__(
            "New proxy",
            setting_proxy=True,
            required=required,  # we need to treat the input as not required when the user presses the remove button
        )


class ProxyNotSet(ProxyBaseContainer):
    def compose(self) -> ComposeResult:
        yield Notice(
            "setting proxy will delete your witnesses votes and deactivate your proposal votes",
        )
        with SectionScrollable("Set proxy for the account"):
            yield CurrentProxy("Proxy not set")
            yield NewProxyInput(required=True)
            with Container(id="set-button-container"):
                yield CliveButton("Set proxy", id_="set-proxy-button", variant="success")


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
        with SectionScrollable("Modify proxy for the account"):
            yield CurrentProxy(self._current_proxy)
            yield NewProxyInput(required=False)
            with Horizontal(id="modify-proxy-buttons"):
                yield CliveButton("Change proxy", variant="success", id_="set-proxy-button")
                yield CliveButton("Remove proxy", variant="error", id_="remove-proxy-button")


class Proxy(TabPane, CliveWidget):
    """TabPane with all content about proxy."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType):
        super().__init__(title=title)
        self._current_proxy = self.app.world.profile_data.working_account.data.proxy

    def on_mount(self) -> None:
        self.watch(self.app.world, "profile_data", self.sync_when_proxy_changed)

    @property
    def new_proxy_input(self) -> NewProxyInput:
        return self.query_one(NewProxyInput)

    def compose(self) -> ComposeResult:
        content = ProxySet(self._current_proxy) if self._current_proxy else ProxyNotSet()
        with ScrollablePart():
            yield content

    @on(Button.Pressed, "#set-proxy-button")
    def set_new_proxy(self) -> None:
        if not self.new_proxy_input.validate_passed():
            # we need to exclusively validate the input when set button is pressed, because the input is not validated
            # when the user presses the remove button - that's also why we can't use required=True in the input init
            return

        new_proxy = self.new_proxy_input.value_or_error  # already validated
        self.app.push_screen(AccountWitnessProxy(new_proxy=new_proxy))

    @on(Button.Pressed, "#remove-proxy-button")
    def remove_proxy(self) -> None:
        self.app.push_screen(AccountWitnessProxy(new_proxy=None))

    def sync_when_proxy_changed(self) -> None:
        proxy_profile_data = self.app.world.profile_data.working_account.data.proxy
        if self._current_proxy != proxy_profile_data:
            self._current_proxy = proxy_profile_data

            content = ProxySet(self._current_proxy) if self._current_proxy else ProxyNotSet()

            with self.app.batch_update():
                self.query_one(ProxyBaseContainer).remove()
                self.query_one(ScrollablePart).mount(content)
