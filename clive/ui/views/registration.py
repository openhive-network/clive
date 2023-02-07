from __future__ import annotations

from clive.ui.components.registration_buttons import RegistrationButtons
from clive.ui.components.registration_form import RegistrationForm
from clive.ui.views.button_based import ButtonsBased


class Registration(ButtonsBased[RegistrationForm, RegistrationButtons]):
    def __init__(self) -> None:
        super().__init__(RegistrationForm(self), RegistrationButtons(self))
