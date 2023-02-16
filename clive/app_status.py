from __future__ import annotations

from copy import deepcopy

from clive.enums import AppMode


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

        from clive.ui.app import clive_app

        clive_app.app_status = deepcopy(self)

    @property
    def current_profile(self) -> str:
        return self.__current_profile

    @current_profile.setter
    def current_profile(self, value: str) -> None:
        self.__current_profile = value

    def is_active(self) -> bool:
        return self.__mode is AppMode.ACTIVE

    def is_inactive(self) -> bool:
        return self.__mode is AppMode.INACTIVE
