from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.profile_data import ProfileData
from clive.__private.ui.create_profile.create_profile import CreateProfileForm
from clive.__private.ui.manage_authorities import NewAuthorityForm
from clive.__private.ui.quit.quit import Quit
from clive.__private.ui.set_account.set_account import SetAccount
from clive.__private.ui.set_node_address.set_node_address import SetNodeAddressForm
from clive.__private.ui.shared.dedicated_form_screens.finish_form_screen import FinishFormScreen
from clive.__private.ui.shared.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.__private.ui.shared.form import Form, ScreenBuilder

if TYPE_CHECKING:
    from collections.abc import Iterator


class OnboardingWelcomeScreen(WelcomeFormScreen[ProfileData]):
    def _cancel(self) -> None:
        self.app.push_screen(Quit())


class OnboardingFinishScreen(FinishFormScreen[ProfileData]):
    def action_finish(self) -> None:
        self.app.world.profile_data = self.context
        super().action_finish()


class Onboarding(Form[ProfileData]):
    @property
    def context(self) -> ProfileData:
        return self.__context

    def register_screen_builders(self) -> Iterator[ScreenBuilder[ProfileData]]:
        yield CreateProfileForm
        yield SetNodeAddressForm
        yield SetAccount
        yield NewAuthorityForm

    def create_welcome_screen(self) -> ScreenBuilder[ProfileData]:
        return lambda owner: OnboardingWelcomeScreen(
            owner,
            "Let's start onboarding!\nIn any moment you can press the `[blue]?[/]` button to see the help page.",
        )

    def create_finish_screen(self) -> ScreenBuilder[ProfileData]:
        return lambda owner: OnboardingFinishScreen(owner, "Now you are ready to enter Clive, enjoy!")

    def _rebuild_context(self) -> None:
        self.__context = ProfileData(ProfileData.ONBOARDING_PROFILE_NAME)

    def _skip_during_push_screen(self) -> list[ScreenBuilder[ProfileData]]:
        screens_to_skip: list[ScreenBuilder[ProfileData]] = []

        # skip NewAuthorityForm if there is no working account set
        if not self.context.is_working_account_set():
            screens_to_skip.append(NewAuthorityForm)

        return screens_to_skip
