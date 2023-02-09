from __future__ import annotations

from clive.enums import AppMode
from clive.ui.get_view_manager import get_view_manager
from clive.ui.view_switcher import switch_view


class AppStatus:
    """A class that holds information about the current state of an application."""

    def __init__(self) -> None:
        self.__mode = AppMode.INACTIVE
        self.__current_profile = "last_used_profile"

    @property
    def mode(self) -> AppMode:
        return self.__mode

    @mode.setter
    def mode(self, value: AppMode) -> None:
        self.__mode = value

    @property
    def current_profile(self) -> str:
        return self.__current_profile

    @current_profile.setter
    def current_profile(self, value: str) -> None:
        self.__current_profile = value

    def is_active(self) -> bool:
        return self.__mode == AppMode.ACTIVE

    def is_inactive(self) -> bool:
        return self.__mode == AppMode.INACTIVE

    def activate(self) -> None:
        switch_view("login")

    def deactivate(self) -> None:
        self.mode = AppMode.INACTIVE

        input_field = get_view_manager().floats.prompt_float.input_field
        input_field.prompt_text = input_field.DEACTIVATED_PROMPT

        switch_view("dashboard")


app_status = AppStatus()
