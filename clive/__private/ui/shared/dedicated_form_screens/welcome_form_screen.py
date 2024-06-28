from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.widgets import Static

from clive.__private.storage.contextual import ContextT
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FirstFormScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class WelcomeTitle(Static):
    """Title of the welcome screen."""


class WelcomeFormScreen(BaseScreen, FirstFormScreen[ContextT]):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]

    def __init__(self, owner: Form[ContextT], title: str) -> None:
        self.__title = title
        super().__init__(owner)

    def create_main_panel(self) -> ComposeResult:
        system_color = "cyan"
        shortcut_styling = "yellow italic"

        title = "Select text, copy and paste inside Terminal"
        select_desc = f"To select some text hold [{shortcut_styling}]Shift[/] while you click and drag."

        copy_paste_desc = (
            "Copy/Paste action shortcuts depend on the environment (mainly terminal)"
            " in which Clive was launched. You may check:"
        )

        on_windows_text = (
            f"  > On [{system_color}]Linux[/]:"
            f" [{shortcut_styling}]Ctrl+Shift+C[/] / [{shortcut_styling}]Ctrl+Shift+V[/]"
        )
        on_llinux_text = (
            f"  > On [{system_color}]Windows[/]: [{shortcut_styling}]Ctrl+C[/] / [{shortcut_styling}]Ctrl+V[/]"
        )
        last_hope_text = (
            f"If none of the above works, you may also try"
            f" [{shortcut_styling}]Ctrl+Insert[/] / [{shortcut_styling}]Shift+Insert[/]."
        )
        otherwise_text = (
            "Otherwise, you should check this for your environment/terminal as it is often quite specific"
            " or configurable and we're unable to indicate a universal solution."
        )

        with DialogContainer("welcome"):
            yield WelcomeTitle(self.__title)
            with Section(title):
                yield Static(select_desc)
                yield Static()
                yield Static(copy_paste_desc)
                yield Static(on_llinux_text)
                yield Static(on_windows_text)
                yield Static(last_hope_text)
                yield Static(otherwise_text)
            yield CliveButton("Start!", id_="welcome-button-start")

    @on(CliveButton.Pressed, "#welcome-button-start")
    async def begin(self) -> None:
        await self.action_next_screen()
