from __future__ import annotations

from typing import TYPE_CHECKING, Literal, cast

from textual.binding import Binding
from textual.suggester import SuggestFromList

from clive.__private.ui.widgets.inputs.text_input import TextInput

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class KeyOrAccountSuggester(SuggestFromList):
    def __init__(self, suggestions: Iterable[str]) -> None:
        super().__init__(suggestions)
        self.cache = None
        self._matched: list[str] = []
        self._index: int = 0

    @property
    def current_suggestion(self) -> str | None:
        if self._matched:
            return self._matched[self._index]
        return None

    async def get_suggestion(self, value: str) -> str | None:
        new_matches = self._match(value)

        if not new_matches:
            self._matched = []
            self.reset_selection()
            return None

        if new_matches != self._matched:
            self._matched = new_matches
            self.reset_selection()
        return self.current_suggestion

    def next_selection(self) -> None:
        self._index = (self._index + 1) % len(self._matched)

    def previous_selection(self) -> None:
        self._index = (self._index - 1 + len(self._matched)) % len(self._matched)

    def reset_selection(self) -> None:
        self._index = 0

    def _match(self, value: str) -> list[str]:
        return [
            self._suggestions[i] for i, suggestion in enumerate(self._for_comparison) if suggestion.startswith(value)
        ]


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
        if not self.input.suggester or self.is_empty:
            return

        suggester = cast("KeyOrAccountSuggester", self.input.suggester)
        suggester.next_selection() if mode == "next" else suggester.previous_selection()
        self.run_worker(suggester._get_suggestion(self.input, self.value_raw))
