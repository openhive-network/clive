from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding

from clive.__private.core.profile import Profile
from clive.__private.ui.onboarding.create_profile_form import CreateProfileForm
from clive.__private.ui.onboarding.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.__private.ui.onboarding.form import Form, ScreenBuilder
from clive.__private.ui.onboarding.new_key_alias_form import NewKeyAliasForm
from clive.__private.ui.onboarding.set_account import SetAccount
from clive.__private.ui.styling import colorize_shortcut

if TYPE_CHECKING:
    from collections.abc import Iterator


class OnboardingWelcomeScreen(WelcomeFormScreen[Profile]):
    BINDINGS = [Binding("escape", "dummy", show=False)]

    def __init__(self, owner: Form[Profile]) -> None:
        super().__init__(
            owner,
            f"Let's start onboarding!\n"
            f"In any moment you can press the {colorize_shortcut('F1')} button to see the Help page.",
        )


class Onboarding(Form[Profile]):
    ONBOARDING_PROFILE_NAME: Final[str] = "onboarding"

    @property
    def context(self) -> Profile:
        return self.__context

    def register_screen_builders(self) -> Iterator[ScreenBuilder[Profile]]:
        yield CreateProfileForm
        yield SetAccount
        yield NewKeyAliasForm

    def create_welcome_screen(self) -> ScreenBuilder[Profile]:
        return lambda owner: OnboardingWelcomeScreen(owner)

    def _rebuild_context(self) -> None:
        self.__context = Profile(self.ONBOARDING_PROFILE_NAME)

    def _skip_during_push_screen(self) -> list[ScreenBuilder[Profile]]:
        screens_to_skip: list[ScreenBuilder[Profile]] = []

        # skip NewKeyAliasForm if there is no working account set
        if not self.context.accounts.has_working_account:
            screens_to_skip.append(NewKeyAliasForm)

        return screens_to_skip
