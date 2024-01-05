from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Button, Static, TabPane

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.operations.raw.account_witness_proxy.account_witness_proxy import AccountWitnessProxy
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput

if TYPE_CHECKING:
    from rich.text import TextType
    from textual.app import ComposeResult


class ScrollablePart(ScrollableContainer, can_focus=False):
    pass


class Proxy(TabPane, CliveWidget):
    """TabPane with all content about proxy."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    def __init__(self, title: TextType):
        super().__init__(title=title)
        self.__proxy_input = AccountNameInput()
        self.__current_proxy = self.app.world.profile_data.working_account.data.proxy

    @property
    def new_proxy(self) -> str | None:
        return self.__proxy_input.value

    def compose(self) -> ComposeResult:
        content = self.__compose_proxy_set if self.__current_proxy else self.__compose_proxy_not_set
        with ScrollablePart():
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
