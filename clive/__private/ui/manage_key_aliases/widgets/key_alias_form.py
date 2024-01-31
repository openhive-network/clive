from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, ClassVar

from textual.containers import Grid, ScrollableContainer
from textual.message import Message
from textual.widgets import Static

from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.contextual import Contextual
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.inputs.public_key_alias_input import PublicKeyAliasInput
from clive.__private.ui.widgets.inputs.text_input import TextInput

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """Container for body."""


class ScrollablePart(ScrollableContainer, can_focus=False):
    pass


class SubTitle(Static):
    pass


class KeyAliasForm(BaseScreen, Contextual[ProfileData], ABC):
    CSS_PATH = [get_relative_css_path(__file__)]

    BIG_TITLE: ClassVar[str] = "Change me in subclass"
    IS_KEY_ALIAS_REQUIRED: ClassVar[bool] = True

    class Changed(Message):
        """Emitted when key alias have been changed."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._key_alias_input = PublicKeyAliasInput(
            value=self._default_key_alias_name(),
            setting_key_alias=True,
            required=self.IS_KEY_ALIAS_REQUIRED,
        )
        self._public_key_input = TextInput(
            "Public key",
            self._default_public_key(),
            placeholder="Public key will be calculated here",
            always_show_title=True,
            required=False,
            validate_on=[],
            disabled=True,
        )

    def create_main_panel(self) -> ComposeResult:
        yield BigTitle(self.BIG_TITLE)
        yield from self._content_after_big_title()
        with ScrollablePart(), Body():
            yield self._key_alias_input
            yield from self._content_after_alias_input()
            yield self._public_key_input

    def _content_after_big_title(self) -> ComposeResult:
        return []

    def _content_after_alias_input(self) -> ComposeResult:
        return []

    def _validate(self) -> None:
        """
        Validates the inputs.

        Raises
        ------
        FailedValidationError: when key alias is not valid.
        """
        self._key_alias_input.validate_with_error()

    def _default_key_alias_name(self) -> str:
        return ""

    def _default_public_key(self) -> str:
        return ""
