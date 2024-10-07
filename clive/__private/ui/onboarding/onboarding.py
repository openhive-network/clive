from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.core.constants.tui.messages import PRESS_HELP_MESSAGE
from clive.__private.core.constants.tui.profile import WELCOME_PROFILE_NAME
from clive.__private.core.node import Node
from clive.__private.core.profile import Profile
from clive.__private.ui.onboarding.context import OnboardingContext
from clive.__private.ui.onboarding.create_profile_form import CreateProfileForm
from clive.__private.ui.onboarding.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.__private.ui.onboarding.form import Form, ScreenBuilder
from clive.__private.ui.onboarding.new_key_alias_form import NewKeyAliasForm
from clive.__private.ui.onboarding.set_account import SetAccount

if TYPE_CHECKING:
    from collections.abc import Iterator


class OnboardingWelcomeScreen(WelcomeFormScreen[OnboardingContext]):
    BINDINGS = [Binding("f1", "help", "Help")]  # help is a hidden global binding, but we want to show it here

    def __init__(self, owner: Form[OnboardingContext]) -> None:
        super().__init__(owner, "Let's start onboarding!\n" + PRESS_HELP_MESSAGE)


class Onboarding(Form[OnboardingContext]):
    @property
    def context(self) -> OnboardingContext:
        return self.__context

    def register_screen_builders(self) -> Iterator[ScreenBuilder[OnboardingContext]]:
        yield CreateProfileForm
        yield SetAccount
        yield NewKeyAliasForm

    def create_welcome_screen(self) -> ScreenBuilder[OnboardingContext]:
        return lambda owner: OnboardingWelcomeScreen(owner)

    def _rebuild_context(self) -> None:
        profile = Profile.create(WELCOME_PROFILE_NAME)
        self.__context = OnboardingContext(profile, Node(profile))

    def _skip_during_push_screen(self) -> list[ScreenBuilder[OnboardingContext]]:
        screens_to_skip: list[ScreenBuilder[OnboardingContext]] = []

        # skip NewKeyAliasForm if there is no working account set
        if not self.context.profile.accounts.has_working_account:
            screens_to_skip.append(NewKeyAliasForm)

        return screens_to_skip
