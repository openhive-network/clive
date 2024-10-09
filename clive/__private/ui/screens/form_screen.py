from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding

from clive.__private.core.contextual import ContextT, Contextual
from clive.__private.core.profile import Profile
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.onboarding.navigation_buttons import NextScreenButton, PreviousScreenButton
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from clive.__private.ui.onboarding.form import Form


class FormScreenBase(CliveScreen, Contextual[ContextT]):
    BINDINGS = [Binding("f1", "help", "Help")]

    def __init__(self, owner: Form[ContextT]) -> None:
        self._owner = owner
        super().__init__()

    @property
    def context(self) -> ContextT:
        return self._owner.context


class FirstFormScreen(FormScreenBase[ContextT]):
    async def action_next_screen(self) -> None:
        self._owner.action_next_screen()


class LastFormScreen(FormScreenBase[ContextT]):
    BINDINGS = [Binding("escape", "previous_screen", "Previous screen", show=False)]

    @on(PreviousScreenButton.Pressed)
    async def action_previous_screen(self) -> None:
        self._owner.action_previous_screen()


class FormScreen(FirstFormScreen[ContextT], LastFormScreen[ContextT], ABC):
    @on(CliveInput.Submitted)
    @on(NextScreenButton.Pressed)
    async def action_next_screen(self) -> None:
        try:
            await self.apply_and_validate()
        except FormValidationError as e:
            self.validation_failure(e)
        else:
            await super().action_next_screen()

    def validation_failure(self, exception: FormValidationError) -> None:
        self.notify(f"Data validated with error, reason: {exception.reason}", severity="error")

    @abstractmethod
    async def apply_and_validate(self) -> None:
        """Perform its actions and raise FormValidationError if some input is invalid."""


class FinishOnboardingFormScreen(FormScreen[Profile]):
    async def action_finish(self) -> None:
        self._owner.add_post_action(self.app.update_data_from_node_asap)

        profile = self.context
        profile.enable_saving()
        self.world.profile = profile
        await self._owner.execute_post_actions()

        if self.app_state.is_unlocked:
            await self.app.switch_screen("dashboard_unlocked")
        else:
            await self.app.switch_screen("dashboard_locked")

        self.profile.save()
