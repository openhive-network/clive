from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal
from textual.validation import Integer
from textual.widgets import Button, Checkbox, Static

from clive.__private.core.constants.tui.messages import PRESS_HELP_MESSAGE
from clive.__private.core.profile import Profile
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.clive_basic.clive_select import CliveSelect
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.password_input import PasswordInput

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SelectProfile(CliveSelect[str], CliveWidget):
    def __init__(self, *, disabled: bool = False) -> None:
        profiles = self.world.profile.list_profiles()
        super().__init__([(profile, profile) for profile in profiles], allow_blank=False, disabled=disabled)


class LockAfterTime(Horizontal):
    DEFAULT_CSS = """
    LockAfterTime {
        margin-bottom: 1;
        height: auto;

        Checkbox {
            width: auto;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Checkbox("Stay unlocked?", value=True)
        yield IntegerInput(
            "Lock countdown (min)",
            value=5,
            always_show_title=True,
            validators=[Integer(minimum=1)],
            id="unlock-time-input",
        )

    @property
    def is_valid(self) -> bool:
        return self._lock_after_time_input.validate_passed()

    @property
    def lock_duration(self) -> timedelta | None:
        if not self.is_valid or self._checkbox.value:
            return None

        return timedelta(minutes=self._lock_after_time_input.value_or_error)

    def on_mount(self) -> None:
        self.watch(self._checkbox, "value", self._change_input_state)

    @property
    def _checkbox(self) -> Checkbox:
        return self.query_exactly_one(Checkbox)

    @property
    def _lock_after_time_input(self) -> IntegerInput:
        return self.query_exactly_one(IntegerInput)

    def _change_input_state(self, value: bool) -> None:  # noqa: FBT001
        self._lock_after_time_input.display = not value


class Unlock(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]
    SHOW_RAW_HEADER = True

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("welcome again!"):
            yield Static(PRESS_HELP_MESSAGE, id="press-help-message")
            yield SelectProfile(disabled=Profile.is_only_one_profile_saved())
            yield PasswordInput()
            yield LockAfterTime()
            yield CliveButton("Unlock", id_="unlock-button", variant="success")
            yield Static("OR", id="or-static")
            yield CliveButton("Create a new profile", id_="new-profile-button")

    @on(Button.Pressed, "#unlock-button")
    @on(CliveInput.Submitted)
    async def unlock(self) -> None:
        password_input = self.query_exactly_one(PasswordInput)
        select_profile = self.query_exactly_one(SelectProfile)
        lock_after_time = self.query_exactly_one(LockAfterTime)

        if not password_input.validate_passed() or not lock_after_time.is_valid:
            return

        if not (
            await self.commands.unlock(
                profile_name=select_profile.value_ensure,
                password=password_input.value_or_error,
                permanent=lock_after_time.lock_duration is None,
                time=lock_after_time.lock_duration,
            )
        ).success:
            return

        self.world.profile = self.profile.load(select_profile.value_ensure)
        await self.app.switch_mode("dashboard")
        self._remove_welcome_modes()
        self.app.update_alarms_data_asap_on_newest_node_data()

    @on(Button.Pressed, "#new-profile-button")
    async def create_new_profile(self) -> None:
        await self.app.switch_mode("create_profile")

    def _remove_welcome_modes(self) -> None:
        self.app.remove_mode("unlock")
        self.app.remove_mode("create_profile")
