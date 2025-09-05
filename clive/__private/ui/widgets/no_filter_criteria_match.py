from __future__ import annotations

from clive.__private.ui.widgets.no_content_available import NoContentAvailable


class NoFilterCriteriaMatch(NoContentAvailable):
    def __init__(self, items_name: str = "items") -> None:
        message = f"There are no {items_name} that match the filter criteria."
        super().__init__(message)
