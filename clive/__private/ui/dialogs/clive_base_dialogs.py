from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal

from textual import on
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.events import Click
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

    @on(Click)
    def close_dialog(self, event: Click) -> None:
        """Close the Dialog if the user clicks outside the modal content."""
        if self.get_widget_at(event.screen_x, event.screen_y)[0] is self:
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

    async def confirm_dialog(self) -> None:
        """Confirm the dialog which means try to perform the action and close the dialog if successful."""
        is_confirmed = await self._perform_confirmation()
        if is_confirmed:
            self.post_message(self.Confirmed())
            self._close_when_confirmed()

    async def cancel_dialog(self) -> None:
        """Cancel the dialog which means close the dialog without performing any action."""
        self._close_when_cancelled()

    async def _perform_confirmation(self) -> bool:
        """Perform the action of the dialog and return True if it was successful."""
        return True

    def _close_when_confirmed(self) -> None:
        self.dismiss()

    def _close_when_cancelled(self) -> None:
        self.dismiss()

    @on(CliveInput.Submitted)
    @on(ConfirmOneLineButton.Pressed)
    async def _confirm_with_event(self) -> None:
        """By default, pressing the confirm button or submitting the input will confirm the dialog."""
        await self.confirm_dialog()

    @on(CancelOneLineButton.Pressed)
    async def _cancel_with_button(self) -> None:
        """By default, pressing the cancel button will cancel the dialog."""
        await self.cancel_dialog()

    async def _action_cancel(self) -> None:
        """By default, pressing the cancel key binding will cancel the dialog."""
        await self.cancel_dialog()


class CliveInfoDialog(CliveBaseDialog[None], ABC):
    BINDINGS = [Binding("escape", "close", "Close")]

    def create_buttons_content(self) -> ComposeResult:
        yield CloseOneLineButton()

    async def _close(self) -> None:
        """Close the dialog without performing any action."""
        self.dismiss()

    @on(CloseOneLineButton.Pressed)
    async def _close_with_button(self) -> None:
        """By default, pressing the close button will close the dialog."""
        await self._close()

    async def _action_close(self) -> None:
        """By default, pressing the close key binding will close the dialog."""
        await self._close()
