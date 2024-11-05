from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from textual.widgets import Static

from clive.__private.core.contextual import Contextual
from clive.__private.core.profile import Profile
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.onboarding.context import OnboardingContext
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from clive.__private.ui.widgets.inputs.public_key_alias_input import PublicKeyAliasInput
from clive.__private.ui.widgets.section import SectionScrollable

if TYPE_CHECKING:
    from textual.app import ComposeResult

KeyAliasFormContextT = TypeVar("KeyAliasFormContextT", Profile, OnboardingContext)


class SubTitle(Static):
    pass


class KeyAliasForm(BaseScreen, Contextual[KeyAliasFormContextT], ABC):
    CSS_PATH = [get_relative_css_path(__file__)]

    IS_KEY_ALIAS_REQUIRED: ClassVar[bool] = True
    SECTION_TITLE: ClassVar[str] = "Change me in subclass"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._key_alias_input = PublicKeyAliasInput(
            value=self._default_key_alias_name(),
            setting_key_alias=True,
            key_manager=self._get_context_profile().keys,
            required=self.IS_KEY_ALIAS_REQUIRED,
        )
        self._public_key_input = LabelizedInput(
            "Public key", self._default_public_key() or "will be calculated here", id="public-key"
        )

    def create_main_panel(self) -> ComposeResult:
        yield from self._content_after_big_title()
        with SectionScrollable(self.SECTION_TITLE):
            yield self._key_alias_input
            yield from self._content_after_alias_input()
            yield self._public_key_input

    def _get_context_profile(self) -> Profile:
        if isinstance(self.context, Profile):
            return self.context
        return self.context.profile

    def _content_after_big_title(self) -> ComposeResult:
        return []

    def _content_after_alias_input(self) -> ComposeResult:
        return []

    def _validate(self) -> None:
        """
        Validate the inputs.

        Raises
        ------
        FailedValidationError: when key alias is not valid.
        """
        self._key_alias_input.validate_with_error()

    def _default_key_alias_name(self) -> str:
        return ""

    def _default_public_key(self) -> str:
        return ""
