from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.suggester import SuggestFromList

from clive.__private.ui.widgets.inputs.account_name_input import AccountNameInput
from clive.__private.validators.authority_entry_validator import AuthorityEntryValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class KeySuggester(SuggestFromList):
    def __init__(self) -> None:
        self._INITIAL_SUGGESTIONS: Final = ["STM51o23o", "STMw3rO2Ac", "STMoP2qn7g256", "STMp21A2nbT3h7", "abit"]
        super().__init__(suggestions=self._INITIAL_SUGGESTIONS)
        self._suggestion_start_index = 0

    def decrement_suggestion_start_index(self) -> None:
        self._reset_suggestions()
        if self._suggestion_start_index <= 0:
            self._suggestion_start_index = len(self._suggestions) - 1
        else:
            self._suggestion_start_index -= 1
        self._suggestions = self._suggestions[self._suggestion_start_index :]
        self._for_comparison = self._suggestions

    def increment_suggestion_start_index(self) -> None:
        self._reset_suggestions()
        if self._suggestion_start_index >= len(self._suggestions) - 1:
            self._suggestion_start_index = 0
        else:
            self._suggestion_start_index += 1
        self._suggestions = self._suggestions[self._suggestion_start_index :]
        self._for_comparison = self._suggestions

    def _reset_suggestions(self) -> None:
        self._suggestions = self._INITIAL_SUGGESTIONS


class AuthorityInput(AccountNameInput):
    """An input for authority entry - Hive account name or public key."""

    BINDINGS = [
        Binding("up", "suggest_next", "Suggest next", show=False),
        Binding("down", "suggest_previous", "Suggest previous", show=False),
    ]

    def __init__(
        self,
        title: str = "Authority entry account, public key or private key",
        value: str | None = None,
        placeholder: str = "",
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        show_known_account: bool = True,
        show_bad_account: bool = True,
        validators: Validator | Iterable[Validator] | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            title=title,
            value=value,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            validators=validators or [AuthorityEntryValidator()],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._show_known_account = show_known_account
        self._show_bad_account = show_bad_account
        self.input.suggester = KeySuggester()

    async def action_suggest_next(self) -> None:
        assert self.input.suggester is not None, "Suggester is not assigned to input."
        self.input.suggester.increment_suggestion_start_index()  # type: ignore[attr-defined]
        suggestion = await self.input.suggester.get_suggestion(self.input.value)
        if suggestion:
            self.input._suggestion = suggestion
        else:
            return

    async def action_suggest_previous(self) -> None:
        assert self.input.suggester is not None, "Suggester is not assigned to input."
        self.input.suggester.decrement_suggestion_start_index()  # type: ignore[attr-defined]
        suggestion = await self.input.suggester.get_suggestion(self.input.value)
        if suggestion:
            self.input._suggestion = suggestion
        else:
            return
