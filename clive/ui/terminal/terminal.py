from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Input, Static, TextLog

from clive.ui.widgets.clive_widget import CliveWidget
from clive.ui.widgets.modal import Modal

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import ComposeResult

    from clive.ui.app_state import AppState


class Logs(TextLog):
    def __init__(self) -> None:
        super().__init__(wrap=True, highlight=True, markup=True)

    def on_mount(self) -> None:
        self.watch(self.app, "logs", self.on_logs)  # type: ignore # https://github.com/Textualize/textual/issues/1805

    def on_logs(self, logs: list[RenderableType | object]) -> None:
        last_line_index = len(self.lines)
        for log in logs[last_line_index:]:
            self.write(log)


class CommandLinePrompt(Static, CliveWidget):
    INACTIVE_PROMPT: Final[str] = " 🔒 >>>:"
    ACTIVE_PROMPT: Final[str] = " 🔑 ###:"

    def __init__(self) -> None:
        super().__init__(self.INACTIVE_PROMPT)

    def on_mount(self) -> None:
        self.watch(self.app, "app_state", self.on_app_state)  # type: ignore # https://github.com/Textualize/textual/issues/1805

    def on_app_state(self, _: AppState) -> None:
        self.update(self.get_current_prompt())

    def get_current_prompt(self) -> str:
        return self.ACTIVE_PROMPT if self.app.app_state.is_active() else self.INACTIVE_PROMPT


class CommandLineInput(Input, CliveWidget):
    def __init__(self) -> None:
        super().__init__(placeholder="Enter command...")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_input = event.value

        if raw_input:
            self.app.write(raw_input, message_type="input")
        self.value = ""


class CommandLine(Widget):
    def compose(self) -> ComposeResult:
        yield CommandLinePrompt()
        yield CommandLineInput()

    def on_descendant_focus(self) -> None:
        self.query_one(CommandLinePrompt).add_class("active-prompt")

    def on_descendant_blur(self) -> None:
        self.query_one(CommandLinePrompt).remove_class("active-prompt")


class Terminal(Modal, Container):
    def __init__(self) -> None:
        super().__init__(classes="-hidden")

    def compose(self) -> ComposeResult:
        yield Logs()
        yield CommandLine()

    def on_mount(self) -> None:
        self.watch(self.app, "terminal_expanded", self.on_terminal_expanded)  # type: ignore # https://github.com/Textualize/textual/issues/1805

    def on_terminal_expanded(self, expanded: bool) -> None:
        if not expanded:
            self.add_class("-hidden")
            self._restore_focus()
        else:
            self.remove_class("-hidden")
            self.query_one(Logs).scroll_end(animate=False)
            self._override_focus()

    def _focus_after_overriding(self) -> None:
        self.query_one(Input).focus()
