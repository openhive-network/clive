from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal

from textual import on
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.clive_screen import ScreenResultT
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.buttons import CancelOneLineButton, CloseOneLineButton, ConfirmOneLineButton
from clive.__private.ui.widgets.inputs.clive_input import CliveInput

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Click


CliveDialogVariant = Literal["default", "error"]


class CliveDialogContent(Vertical):
    """Contains all the content of the dialog."""


class CliveBaseDialog(ModalScreen[ScreenResultT], CliveWidget, AbstractClassMessagePump):
    DEFAULT_CSS = """
    CliveBaseDialog {
        align: center middle;
        background: $background 85%;

        CliveDialogContent {
            border-title-style: bold;
            border-title-color: $text;
            border-title-background: $primary;
            border: $primary outer;
            background: $panel 80%;
            padding: 1;
            width: 50%;
            height: auto;

            &.-error {
                border-title-background: $error;
                border: $error outer;
            }

            #buttons-container {
                align: center top;
                margin-top: 1;
                height: auto;

                OneLineButton {
                    margin: 0 2;
                }
            }
        }
    }
    """

    variant: CliveDialogVariant = reactive("default", init=False)  # type: ignore[assignment]

    def __init__(
        self,
        border_title: str,
        variant: CliveDialogVariant = "default",
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id_, classes=classes)
        self.content = CliveDialogContent()
        self.content.border_title = border_title
        self.variant = variant

    def compose(self) -> ComposeResult:
        with self.content:
            yield from self.create_dialog_content()

            with Center(), Horizontal(id="buttons-container"):
                yield from self.create_buttons_content()

    def watch_variant(self, old_variant: str, variant: str) -> None:
        self.content.remove_class(f"-{old_variant}")
        self.content.add_class(f"-{variant}")

    def on_click(self, event: Click) -> None:
        if self.get_widget_at(event.screen_x, event.screen_y)[0] is self:
            # Close the screen if the user clicks outside the modal content
            self.dismiss()

    @abstractmethod
    def create_dialog_content(self) -> ComposeResult:
        """Yield all the content for the dialog."""

    @abstractmethod
    def create_buttons_content(self) -> ComposeResult:
        """Yield all the content with buttons."""


class CliveActionDialog(CliveBaseDialog[ScreenResultT], ABC):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    class Confirmed(Message):
        """Inform the dialog that it should be confirmed."""

    def __init__(
        self,
        border_title: str,
        confirm_button_label: str = ConfirmOneLineButton.DEFAULT_LABEL,
        variant: CliveDialogVariant = "default",
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(border_title=border_title, variant=variant, id_=id_, classes=classes)
        self._confirm_button_text = confirm_button_label

    def create_buttons_content(self) -> ComposeResult:
        yield ConfirmOneLineButton(self._confirm_button_text)
        yield CancelOneLineButton()

    @on(CliveInput.Submitted)
    @on(ConfirmOneLineButton.Pressed)
    async def confirm_dialog(self) -> None:
        self.post_message(self.Confirmed())

    @on(CancelOneLineButton.Pressed)
    def action_cancel(self) -> None:
        self.app.pop_screen()


class CliveInfoDialog(CliveBaseDialog[ScreenResultT], ABC):
    BINDINGS = [Binding("escape", "close", "Close")]

    def create_buttons_content(self) -> ComposeResult:
        yield CloseOneLineButton()

    @on(CloseOneLineButton.Pressed)
    def action_close(self) -> None:
        self.app.pop_screen()
