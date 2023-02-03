from clive.ui.get_view_manager import get_view_manager
from clive.ui.view_switcher import switch_view


class AppStatus:
    """A class that holds information about the current state of an application."""

    def __init__(self) -> None:
        self.__active_mode = False
        self.__current_profile = "last_used_profile"

    @property
    def active_mode(self) -> bool:
        return self.__active_mode

    @active_mode.setter
    def active_mode(self, value: bool) -> None:
        self.__active_mode = value

    @property
    def current_profile(self) -> str:
        return self.__current_profile

    @current_profile.setter
    def current_profile(self, value: str) -> None:
        self.__current_profile = value

    def activate(self) -> None:
        switch_view("login")

    def deactivate(self) -> None:
        self.active_mode = False

        input_field = get_view_manager().floats.prompt_float.input_field
        input_field.set_prompt_text(input_field.DEACTIVATED_PROMPT)

        switch_view("dashboard")


app_status = AppStatus()
