from __future__ import annotations

from clive.ui.components.login_buttons import LoginButtons
from clive.ui.components.login_form import LoginForm
from clive.ui.views.button_based import ButtonsBased


class Login(ButtonsBased[LoginForm, LoginButtons]):
    def __init__(self) -> None:
        super().__init__(LoginForm(self), LoginButtons(self))
