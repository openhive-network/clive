from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from textual.containers import Grid, ScrollableContainer
from textual.message import Message
from textual.widgets import Input, Static

from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.contextual import Contextual
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """Container for body."""


class ScrollablePart(ScrollableContainer):
    pass


class SubTitle(Static):
    pass


class AuthorityForm(BaseScreen, Contextual[ProfileData], ABC):
    class AuthoritiesChanged(Message):
        """Emitted when authorities have been changed."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._key_alias_input = Input(self._default_authority_name(), placeholder="e.g. My active key")
        self._public_key_input = Input(
            self._default_public_key(), placeholder="Public key will be calculated here", disabled=True
        )

    @property
    def _key_alias_raw(self) -> str:
        return self._key_alias_input.value

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle(self._title())
            yield from self._content_after_big_title()
            with ScrollablePart(), Body():
                yield Static("Key alias:", classes="label")
                yield self._key_alias_input
                yield from self._content_after_alias_input()
                yield Static("Public key:", classes="label")
                yield self._public_key_input

    def _content_after_big_title(self) -> ComposeResult:
        return []

    def _content_after_alias_input(self) -> ComposeResult:
        return []

    def _validate_with_notification(self, *, reraise_exception: bool = False) -> bool:
        """
        Validate the form and show a notification if there are any errors.

        Returns True if the form is valid, False otherwise.

        Info
            If reraise_exception is True, the exception will be reraised after showing the notification.
        """
        try:
            self._validate()
        except FormValidationError as error:
            Notification(
                f"Failed the validation process! Could not continue. Reason: {error.reason}", category="error"
            ).show()
            if reraise_exception:
                raise
            return False
        else:
            return True

    @abstractmethod
    def _validate(self) -> None:
        """Should raise FormValidationError if validation fails."""

    def _title(self) -> str:
        return ""

    def _default_authority_name(self) -> str:
        return ""

    def _default_public_key(self) -> str:
        return ""
