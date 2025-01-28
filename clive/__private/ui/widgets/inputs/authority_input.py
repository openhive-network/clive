from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from textual.binding import Binding
from textual.suggester import SuggestFromList

from clive.__private.ui.widgets.inputs.text_input import TextInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class KeyOrAccountSuggester(SuggestFromList):
    def __init__(self, suggestions: list[str]) -> None:
        super().__init__(suggestions=suggestions)
        self._initial_suggestions = suggestions
        self._suggestion_start_index = -1

    def reduce_suggestions(
        self, *, input_value: str, current_suggestion: str, mode: Literal["next", "previous"]
    ) -> None:
        self._reset_suggestions()
        self._suggestion_start_index = (
            self._get_index_of_next_suggestion(input_value=input_value, current_suggestion=current_suggestion)
            if mode == "next"
            else self._get_index_of_previous_suggestion(input_value=input_value, current_suggestion=current_suggestion)
        )
        self._suggestions = self._suggestions[self._suggestion_start_index :]
        self._for_comparison = self._suggestions

    def _get_index_of_suggestion(self, suggestion: str) -> int:
        if suggestion in self._initial_suggestions:
            return self._initial_suggestions.index(suggestion)
        raise ValueError(f"Suggestion '{suggestion}' not found in the list of initial suggestions.")

    def _get_all_matching_suggestions(self, input_value: str) -> list[str]:
        """Get all suggestions that match the given value."""
        return [suggestion for suggestion in self._for_comparison if suggestion.startswith(input_value)]

    def _get_index_of_next_suggestion(self, *, input_value: str, current_suggestion: str) -> int:
        all_matched_suggestions = self._get_all_matching_suggestions(input_value)
        if all_matched_suggestions and current_suggestion in all_matched_suggestions:
            current_index = all_matched_suggestions.index(current_suggestion)
            if len(all_matched_suggestions) > 1:
                if current_index == len(all_matched_suggestions) - 1:
                    # if the current suggestion is the last one, return index of the first one
                    return self._get_index_of_suggestion(next(iter(all_matched_suggestions)))
                # if there are more suggestions, return the next one
                return self._get_index_of_suggestion(all_matched_suggestions[current_index + 1])

            # if there is only one suggestion, return its index from the original list
            return self._get_index_of_suggestion(all_matched_suggestions[current_index])
        raise ValueError(f"Suggestion '{current_suggestion}' not found in the list of matched suggestions.")

    def _get_index_of_previous_suggestion(self, *, input_value: str, current_suggestion: str) -> int:
        all_matched_suggestions = self._get_all_matching_suggestions(input_value)
        if all_matched_suggestions and current_suggestion in all_matched_suggestions:
            current_index = all_matched_suggestions.index(current_suggestion)
            if len(all_matched_suggestions) > 1:
                if current_index == 0:
                    # if the current suggestion is the first one, return index of the last one
                    return self._get_index_of_suggestion(all_matched_suggestions[-1])
                # if there are more suggestions, return the previous one
                return self._get_index_of_suggestion(all_matched_suggestions[current_index - 1])

            # if there is only one suggestion, return its index from the original list
            return self._get_index_of_suggestion(all_matched_suggestions[current_index])
        raise ValueError(f"Suggestion '{current_suggestion}' not found in the list of matched suggestions.")

    def _reset_suggestions(self) -> None:
        self._suggestions = self._initial_suggestions
        self._for_comparison = self._initial_suggestions


class AuthorityInput(TextInput):
    """An input for authority entry - Hive account name, public / private key or alias."""

    BINDINGS = [
        Binding("up", "suggest_next", "Suggest next", show=False),
        Binding("down", "suggest_previous", "Suggest previous", show=False),
    ]

    def __init__(
        self,
        title: str = "Authority entry account, public/private key or alias",
        value: str | None = None,
        placeholder: str = "",
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = False,
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
            validators=validators,
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._excluded_suggestions: list[str] = []

    async def action_suggest_next(self) -> None:
        await self._suggest(mode="next")

    async def action_suggest_previous(self) -> None:
        await self._suggest(mode="previous")

    def load_new_suggestions(self, suggestions: list[str]) -> None:
        self.input.suggester = KeyOrAccountSuggester(suggestions)

    async def _suggest(self, mode: Literal["next", "previous"]) -> None:
        current_suggestion = self.input._suggestion
        if current_suggestion == "":
            return
        assert self.input.suggester is not None, "Suggester is not assigned to input."
        current_suggestion = self.input._suggestion
        input_value = self.input.value
        self.input.suggester.reduce_suggestions(  # type: ignore[attr-defined]
            input_value=input_value,
            current_suggestion=current_suggestion,
            mode=mode,
        )
        # get new suggestion after reduction
        suggestion = await self.input.suggester.get_suggestion(self.input.value)
        if suggestion:
            self.input._suggestion = suggestion
