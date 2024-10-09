from __future__ import annotations

from typing import ClassVar

from textual import on

from clive.__private.logger import logger
from clive.__private.ui.onboarding.context import OnboardingContext
from clive.__private.ui.onboarding.form_screen import FormScreen
from clive.__private.ui.onboarding.navigation_buttons import NextScreenButton, PreviousScreenButton
from clive.__private.ui.screens.config.manage_key_aliases.new_key_alias import NewKeyAliasBase
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from clive.__private.ui.widgets.inputs.clive_validated_input import FailedManyValidationError


class NewKeyAliasForm(NewKeyAliasBase[OnboardingContext], FormScreen[OnboardingContext]):
    BIG_TITLE = "Onboarding"
    SUBTITLE = "Optional step, could be done later"
    IS_KEY_ALIAS_REQUIRED: ClassVar[bool] = False
    IS_PRIVATE_KEY_REQUIRED: ClassVar[bool] = False

    @property
    def should_complete_this_step(self) -> bool:
        """NewKeyAliasForm step is optional, to check if it should be skipped use this property."""
        return not self._key_input.is_empty or not self._key_alias_input.is_empty

    @on(PreviousScreenButton.Pressed)
    async def action_previous_screen(self) -> None:
        # We allow just for adding one key during onboarding. Clear old ones because validation could fail.
        self.context.profile.keys.clear_to_import()
        await super().action_previous_screen()

    @on(NextScreenButton.Pressed)
    @on(CliveInput.Submitted)
    async def action_next_screen(self) -> None:
        self.should_finish = True
        if not self.should_complete_this_step:
            # skip validation and apply part
            await self.finish()
            return

        await super().action_next_screen()

    async def validate(self) -> NewKeyAliasForm.ValidationFail | None:
        try:
            self._validate()
        except FailedManyValidationError:
            return self.ValidationFail()
        return None

    async def apply(self) -> None:
        self.context.profile.keys.set_to_import([self._private_key_aliased])
        logger.debug("New private key is waiting to be imported...")
