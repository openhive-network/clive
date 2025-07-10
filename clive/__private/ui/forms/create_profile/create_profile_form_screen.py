from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, cast

from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS
from clive.__private.ui.forms.form_screen import FormScreen

if TYPE_CHECKING:
    from clive.__private.ui.forms.create_profile.create_profile_form import CreateProfileForm


class CreateProfileFormScreen(FormScreen, ABC):
    BINDINGS = [
        CLIVE_PREDEFINED_BINDINGS.help.toggle_help.create(
            action="", description="Help"
        ),  # help is a hidden global binding, but we want to show it here
    ]

    def __init__(self, owner: CreateProfileForm) -> None:
        super().__init__(owner)

    @property
    def owner(self) -> CreateProfileForm:
        return cast("CreateProfileForm", super().owner)
