from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from schemas.__private.hive_fields_basic_schemas import Authority

if TYPE_CHECKING:
    from textual.widgets import Input


class RawOperationBaseScreen(OperationBaseScreen, AbstractClassMessagePump):
    """Base class for all raw operations."""

    @staticmethod
    def _split_auths_fields(auths: str) -> list[tuple[str, int]]:
        """To create valid format of auths like key_auths, to create pydantic operation model."""
        if not auths:
            return []

        valid_auths_format = []

        split_auths = auths.split(";")
        for pair in split_auths:
            string_part, number = pair.split(",")

            string_part = string_part.strip()
            valid_auths_format.append((string_part, int(number)))

        return valid_auths_format

    def _create_authority_field(
        self, weight_threshold_input: Input, account_auths_input: Input, key_auths_input: Input
    ) -> Authority | None:
        if not weight_threshold_input.value:
            return Authority(
                weight_threshold=int(weight_threshold_input.value),
                account_auths=self._split_auths_fields(account_auths_input.value),
                key_auths=self._split_auths_fields(key_auths_input.value),
            )
        return None
