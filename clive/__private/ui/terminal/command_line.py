from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Input, Static

from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from typing_extensions import Self

    from clive.__private.core.app_state import AppState


class CommandLinePrompt(Static, CliveWidget):
    INACTIVE_PROMPT: Final[str] = ">>>:"
    ACTIVE_PROMPT: Final[str] = "###:"

    def __init__(self) -> None:
        super().__init__(self.INACTIVE_PROMPT)

    def on_mount(self) -> None:
        self.watch(self.app.world, "app_state", self.app_state_changed, init=False)

    async def app_state_changed(self, _: AppState) -> None:
        self.update(await self.get_current_prompt())

    async def get_current_prompt(self) -> str:
        return self.ACTIVE_PROMPT if self.app.world.app_state.is_active else self.INACTIVE_PROMPT


class CommandLineInput(Input, CliveWidget):
    def __init__(self) -> None:
        super().__init__(placeholder="Enter command...", id="command-line-input")

    @on(Input.Submitted)
    async def handle_command(self, event: Input.Submitted) -> None:
        raw_input = event.value

        if raw_input:
            await self.app.write(raw_input, message_type="input")
        self.value = ""


class CommandLine(Widget):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    BINDINGS = [
        Binding("escape", "cancel", "Back"),
    ]

    def __init__(self, *, focus_on_cancel: Widget) -> None:
        super().__init__()
        self.__focus_on_cancel = focus_on_cancel

    def compose(self) -> ComposeResult:
        yield CommandLinePrompt()
        yield CommandLineInput()

    def focus(self, _: bool = True) -> Self:
        self.query_one(CommandLineInput).focus()
        return self

    def on_descendant_focus(self) -> None:
        self.query_one(CommandLinePrompt).add_class("--active")

    def on_descendant_blur(self) -> None:
        self.query_one(CommandLinePrompt).remove_class("--active")

    def action_cancel(self) -> None:
        self.__focus_on_cancel.focus()
