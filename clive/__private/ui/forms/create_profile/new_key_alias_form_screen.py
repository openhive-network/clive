from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual import on
from textual.binding import Binding

from clive.__private.logger import logger
from clive.__private.ui.forms.create_profile.create_profile_form_screen import CreateProfileFormScreen
from clive.__private.ui.forms.navigation_buttons import NavigationButtons, PreviousScreenButton
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.config.manage_key_aliases.key_alias_base import NewKeyAliasBase
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    FailedManyValidationError,
)
from clive.__private.ui.widgets.section import SectionScrollable
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult


class NewKeyAliasFormScreen(NewKeyAliasBase, BaseScreen[bool], CreateProfileFormScreen):
    DEFAULT_CSS = """
    NewKeyAliasFormScreen {
        Section {
            margin: 0 4;

            NavigationButtons {
            margin-top: 1;
            }

            #public-key,
            PublicKeyAliasInput {
            margin-top: 1;
            }
        }
    }
    """
    BINDINGS = [
        Binding("f1", "help", "Help"),
        Binding("f2", "load_from_file", "Load from file"),
    ]

    BIG_TITLE = "create profile"
    SUBTITLE = "Optional step, could be done later"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)
        self._key_file_path: Path | None = None

    def create_main_panel(self) -> ComposeResult:
        with SectionScrollable("Add key alias"):
            yield from self._content_after_alias_input()
            yield self._public_key_input
            yield self._key_alias_input
            if not self.app_state.is_unlocked:
                yield NavigationButtons(is_finish=True)
        yield SelectCopyPasteHint()

    @property
    def should_finish(self) -> bool:
        return True

    @on(PreviousScreenButton.Pressed)
    async def action_previous_screen(self) -> None:
        # We allow just for adding one key during create_profile. Clear old ones because validation could fail.
        self.profile.keys.clear_to_import()
        await super().action_previous_screen()

    def action_load_from_file(self) -> None:
        from clive.__private.ui.dialogs import LoadKeyFromFileDialog

        self.app.push_screen(LoadKeyFromFileDialog(), self._load_private_key_from_file)

    def _load_private_key_from_file(self, loaded_private_key: str | None) -> None:
        if loaded_private_key is None:
            return

        self._key_input.input.value = loaded_private_key

    async def validate(self) -> NewKeyAliasFormScreen.ValidationFail | None:
        try:
            self._validate()
        except FailedManyValidationError:
            return self.ValidationFail()
        return None

    async def apply(self) -> None:
        self.profile.keys.set_to_import([self._private_key_aliased])
        logger.debug("New private key is waiting to be imported...")

    def is_step_optional(self) -> bool:
        return self._key_input.is_empty
