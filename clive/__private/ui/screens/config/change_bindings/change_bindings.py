from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding

from clive.__private.ui.dialogs.read_key_dialog import ReadKeyDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import OneLineButton
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ChangeBindings(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    BIG_TITLE = "configuration"
    SUBTITLE = "Change bindings"

    def __init__(self) -> None:
        super().__init__()

    def create_main_panel(self) -> ComposeResult:
        with Section(title="Please choose which binding you would like to change"):
            yield OneLineButton("Show changes", id_="show")
            yield OneLineButton("Apply changes and validate", id_="apply")
            yield OneLineButton("Revert changes", id_="revert")
            yield OneLineButton("Reset to default bindings", id_="reset")
            yield OneLineButton("Example action", id_="example")
            yield OneLineButton("Example action 2", id_="example2")

    @on(OneLineButton.Pressed, "#show")
    async def show(self) -> None:
        return None

    @on(OneLineButton.Pressed, "#apply")
    async def apply(self) -> None:
        return None

    @on(OneLineButton.Pressed, "#revert")
    async def revert(self) -> None:
        return None

    @on(OneLineButton.Pressed, "#reset")
    async def reset(self) -> None:
        return None

    @on(OneLineButton.Pressed, "#example")
    async def example(self) -> None:
        await self.app.push_screen(ReadKeyDialog(description="action example 1"))

    @on(OneLineButton.Pressed, "#example2")
    async def example2(self) -> None:
        await self.app.push_screen(ReadKeyDialog(description="action example 2"))
