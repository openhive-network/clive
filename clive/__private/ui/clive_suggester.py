from __future__ import annotations

from typing import TYPE_CHECKING

from textual.suggester import SuggestFromList

if TYPE_CHECKING:
    from collections.abc import Iterable


class CliveSuggester(SuggestFromList):
    """
    Suggester that can track the position of suggestion selection.

    Can be used mainly for CliveInput - to switch between suggestions by user action.

    Args:
        suggestions: Initial suggestions to fill the suggester with.
    """

    def __init__(self, suggestions: Iterable[str] | None = None) -> None:
        super().__init__(suggestions or [])
        self.cache = None
        self._matched: list[str] = []
        self._index: int = 0

    @property
    def current_suggestion(self) -> str | None:
        if self._matched:
            return self._matched[self._index]
        return None

    def add_suggestion(self, *suggestions: str) -> None:
        self._suggestions.extend(suggestion for suggestion in suggestions if suggestion not in self._suggestions)
        self._for_comparison = (
            self._suggestions if self.case_sensitive else [suggestion.casefold() for suggestion in self._suggestions]
        )

    def clear_suggestions(self) -> None:
        self._suggestions.clear()
        self._for_comparison.clear()
        self._matched.clear()
        self.reset_selection()

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
        if not self._matched:
            return
        self._index = (self._index + 1) % len(self._matched)

    def previous_selection(self) -> None:
        if not self._matched:
            return
        self._index = (self._index - 1 + len(self._matched)) % len(self._matched)

    def reset_selection(self) -> None:
        self._index = 0

    def _match(self, value: str) -> list[str]:
        return [
            self._suggestions[i] for i, suggestion in enumerate(self._for_comparison) if suggestion.startswith(value)
        ]
