from __future__ import annotations

from typing import ClassVar

from textual import on
from textual.binding import Binding

from clive.__private.logger import logger
from clive.__private.ui.dialogs import LoadKeyFromFileDialog
from clive.__private.ui.forms.create_profile.create_profile_form_screen import CreateProfileFormScreen
from clive.__private.ui.forms.navigation_buttons import PreviousScreenButton
from clive.__private.ui.screens.config.manage_key_aliases.new_key_alias import NewKeyAliasBase
from clive.__private.ui.widgets.inputs.clive_validated_input import FailedManyValidationError


class NewKeyAliasFormScreen(NewKeyAliasBase, CreateProfileFormScreen):
    BINDINGS = [Binding("f1", "help", "Help")]
    BIG_TITLE = "create profile"
    SUBTITLE = "Optional step, could be done later"
    IS_PRIVATE_KEY_REQUIRED: ClassVar[bool] = False

    @property
    def should_finish(self) -> bool:
        return True

    @on(PreviousScreenButton.Pressed)
    async def action_previous_screen(self) -> None:
        # We allow just for adding one key during create_profile. Clear old ones because validation could fail.
        self.profile.keys.clear_to_import()
        await super().action_previous_screen()

    def action_load_from_file(self) -> None:
        self.app.push_screen(LoadKeyFromFileDialog(), self._load_private_key_from_file)

    def _load_private_key_from_file(self, loaded_private_key: PrivateKey | None) -> None:
        if loaded_private_key is None:
            return

        self.private_key_input.input.value = loaded_private_key.value

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
