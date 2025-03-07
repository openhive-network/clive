from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.profile import WELCOME_PROFILE_NAME
from clive.__private.core.node import Node
from clive.__private.core.profile import Profile
from clive.__private.ui.forms.create_profile.context import CreateProfileContext
from clive.__private.ui.forms.create_profile.create_profile_form_screen import CreateProfileFormScreen
from clive.__private.ui.forms.create_profile.new_key_alias_form_screen import NewKeyAliasFormScreen
from clive.__private.ui.forms.create_profile.set_account_form_screen import SetAccountFormScreen
from clive.__private.ui.forms.create_profile.welcome_form_screen import CreateProfileWelcomeFormScreen
from clive.__private.ui.forms.form import Form

if TYPE_CHECKING:
    from collections.abc import Iterator

    from clive.__private.ui.forms.form_screen import FormScreenBase


class CreateProfileForm(Form[CreateProfileContext]):
    @property
    def context(self) -> CreateProfileContext:
        return self.__context

    def register_screen_builders(self) -> Iterator[type[FormScreenBase[CreateProfileContext]]]:
        if not Profile.is_any_profile_saved():
            yield CreateProfileWelcomeFormScreen
        yield CreateProfileFormScreen
        yield SetAccountFormScreen
        yield NewKeyAliasFormScreen

    def _rebuild_context(self) -> None:
        profile = Profile.create(WELCOME_PROFILE_NAME)
        self.__context = CreateProfileContext(profile, Node(profile))
