from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, cast

from textual.binding import Binding

from clive.__private.ui.forms.form_screen import FormScreen

if TYPE_CHECKING:
    from clive.__private.ui.forms.create_profile.create_profile_form import CreateProfileForm


class CreateProfileFormScreen(FormScreen, ABC):
    BINDINGS = [Binding("f1", "help", "Help")]

    def __init__(self, owner: CreateProfileForm) -> None:
        super().__init__(owner)

    @property
    def owner(self) -> CreateProfileForm:
        return cast("CreateProfileForm", super().owner)
