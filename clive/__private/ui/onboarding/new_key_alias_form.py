from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from clive.__private.core.profile import Profile
from clive.__private.logger import logger
from clive.__private.ui.screens.config.manage_key_aliases.new_key_alias import NewKeyAliasBase
from clive.__private.ui.screens.form_screen import FormScreen
from clive.__private.ui.widgets.inputs.clive_validated_input import FailedManyValidationError
from clive.exceptions import FormValidationError

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
    def is_key_provided(self) -> bool:
        return bool(self._key_input.value_raw)

    async def apply_and_validate(self) -> None:
        if self.is_key_provided:  # NewKeyAliasForm step is optional, so we can skip it when no key is provided
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
        except FailedManyValidationError as error:
            raise FormValidationError(str(error)) from error
