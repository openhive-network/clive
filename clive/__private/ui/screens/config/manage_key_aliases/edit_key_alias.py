from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.binding import Binding

from clive.__private.core.profile import Profile
from clive.__private.ui.screens.config.manage_key_aliases.widgets.key_alias_form import KeyAliasForm
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    FailedValidationError,
    InputValueError,
)

if TYPE_CHECKING:
    from clive.__private.core.keys import PublicKeyAliased


class EditKeyAlias(KeyAliasForm[Profile]):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f6", "save", "Save"),
    ]

    BIG_TITLE: ClassVar[str] = "Configuration"
    SUBTITLE: ClassVar[str] = "Manage key aliases"
    SECTION_TITLE: ClassVar[str] = "Edit key alias"

    def __init__(self, public_key: PublicKeyAliased) -> None:
        self._public_key = public_key
        super().__init__()

    @property
    def context(self) -> Profile:
        return self.profile

    def action_save(self) -> None:
        try:
            self._validate()
        except FailedValidationError:
            return  # Validation errors are already displayed.
        except InputValueError as error:
            self.notify(str(error), severity="error")
            return

        old_alias = self._public_key.alias
        new_alias = self._key_alias_input.value_or_error
        self.profile.keys.rename(old_alias, new_alias)
        self.notify(f"Key alias `{self._public_key.alias}` was edited.")

        self.app.trigger_profile_watchers()
        self.dismiss()

    def _default_key_alias_name(self) -> str:
        return self._public_key.alias

    def _default_public_key(self) -> str:
        return self._public_key.value
