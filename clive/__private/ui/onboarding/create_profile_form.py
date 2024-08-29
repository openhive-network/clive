from __future__ import annotations

from clive.__private.core.profile import Profile
from clive.__private.ui.screens.create_profile.create_profile import CreateProfileCommon
from clive.__private.ui.screens.form_screen import FormScreen


class CreateProfileForm(CreateProfileCommon, FormScreen[Profile]):
    BIG_TITLE = "onboarding"

    async def apply_and_validate(self) -> None:
        self._owner.clear_post_actions()  # create profile form is a first form, so clear all previously stored actions
        self._owner.add_post_action(*self._create_profile())
