from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.profile import Profile
from clive.__private.logger import logger
from clive.__private.ui.screens.config.manage_key_aliases.new_key_alias import NewKeyAliasBase
from clive.__private.ui.screens.form_screen import FormScreen, FormValidationError
from clive.__private.ui.widgets.inputs.clive_validated_input import FailedManyValidationError

if TYPE_CHECKING:
    from clive.__private.ui.onboarding.form import Form


class NewKeyAliasForm(NewKeyAliasBase, FormScreen[Profile]):
    BIG_TITLE = "Onboarding"
    SUBTITLE = "Optional step, could be done later"
    IS_KEY_ALIAS_REQUIRED: ClassVar[bool] = False
    IS_PRIVATE_KEY_REQUIRED: ClassVar[bool] = False

    def __init__(self, owner: Form[Profile]) -> None:
        super().__init__(owner=owner)

    @property
    def should_complete_this_step(self) -> bool:
        """NewKeyAliasForm step is optional, to check if it should be skipped use this property."""
        return bool(self._key_input.value_raw) or bool(self._key_alias_input.value_raw)

    async def apply_and_validate(self) -> None:
        if not self.should_complete_this_step:
            return

        # We allow just for adding one key during onboarding. Clear old ones because validation could fail.
        self.context.keys.clear_to_import()

        self._validate()
        self.context.keys.set_to_import([self._private_key_aliased])
        logger.debug("New private key is waiting to be imported...")

    def _validate(self) -> None:
        """
        Validate the inputs.

        Converts the FailedManyValidationError to FormValidationError which can be handled by form later.

        Raises
        ------
        FormValidationError: when key alias or private key inputs are invalid.
        """
        try:
            super()._validate()
        except FailedManyValidationError:
            raise FormValidationError from None
