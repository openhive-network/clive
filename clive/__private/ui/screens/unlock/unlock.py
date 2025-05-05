from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from beekeepy.exceptions import InvalidPasswordError
from textual import on
from textual.containers import Horizontal
from textual.validation import Integer
from textual.widgets import Button, Checkbox, Static

from clive.__private.core.constants.tui.messages import PRESS_HELP_MESSAGE
from clive.__private.core.error_handlers.general_error_notificator import GeneralErrorNotificator
from clive.__private.core.profile import Profile
from clive.__private.logger import logger
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
        profiles = Profile.list_profiles()
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
    def should_stay_unlocked(self) -> bool:
        return self._checkbox.value

    @property
    def is_valid(self) -> bool:
        if self.should_stay_unlocked:
            return True

        return self._lock_after_time_input.validate_passed()

    @property
    def lock_duration(self) -> timedelta | None:
        """Return lock duration. None means should stay unlocked (permanent unlock)."""
        if self.should_stay_unlocked:
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
        async def impl() -> None:
            password_input = self.query_exactly_one(PasswordInput)
            select_profile = self.query_exactly_one(SelectProfile)
            lock_after_time = self.query_exactly_one(LockAfterTime)

            if not password_input.validate_passed() or not lock_after_time.is_valid:
                return

            try:
                await self.world.load_profile(
                    profile_name=select_profile.selection_ensure,
                    password=password_input.value_or_error,
                    permanent=lock_after_time.should_stay_unlocked,
                    time=lock_after_time.lock_duration,
                )
            except InvalidPasswordError:
                logger.error(
                    f"Profile `{select_profile.selection_ensure}` was not unlocked "
                    "because entered password is invalid, skipping switching modes"
                )
                return

            # avoid showing notification with wrong password (from previous tries) after unlocking
            invalid_password_error_notification_text = GeneralErrorNotificator.SEARCHED_AND_PRINTED_MESSAGES[
                InvalidPasswordError
            ]
            if self.app.is_notification_present(invalid_password_error_notification_text):
                self.app.clear_notifications()

            await self.app._switch_mode_into_unlocked()

        # Has to be done in a separate task to avoid deadlock.
        # More: https://github.com/Textualize/textual/issues/5008
        self.app.run_worker_with_screen_remove_guard(impl())

    @on(Button.Pressed, "#new-profile-button")
    async def create_new_profile(self) -> None:
        async def impl() -> None:
            await self.app.switch_mode_with_reset("create_profile")

        # Has to be done in a separate task to avoid deadlock.
        # More: https://github.com/Textualize/textual/issues/5008
        self.app.run_worker_with_screen_remove_guard(impl())

    @on(SelectProfile.Changed)
    def clear_password_input(self) -> None:
        self.query_exactly_one(PasswordInput).clear_validation()
