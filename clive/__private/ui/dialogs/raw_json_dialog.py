from __future__ import annotations

import json
from typing import TYPE_CHECKING

from textual.containers import Center
from textual.widgets import Pretty

from clive.__private.models.schemas import convert_to_representation
from clive.__private.ui.dialogs.clive_base_dialogs import CliveInfoDialog
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.models.schemas import OperationBase


class RawJsonDialog(CliveInfoDialog):
    def __init__(self, *, operation: OperationBase) -> None:
        super().__init__("Raw JSON")
        self._operation = operation

    def create_dialog_content(self) -> ComposeResult:
        with Center(), Section():
            yield Pretty(json.loads(self._get_operation_representation_json(self._operation)))

    @staticmethod
    def _get_operation_representation_json(operation: OperationBase) -> str:
        representation = convert_to_representation(operation)
        return representation.json(order="sorted")
