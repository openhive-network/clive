from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.operations.bindings import OperationActionBindings
from clive.__private.ui.operations.operation_base_screen import OperationBaseScreen
from schemas.fields.compound import Authority

if TYPE_CHECKING:
    from clive.__private.ui.widgets.inputs.account_auths_input import AccountAuthsInput
    from clive.__private.ui.widgets.inputs.key_auths_input import KeyAuthsInput
    from clive.__private.ui.widgets.inputs.weight_threshold_input import WeightThresholdInput


class RawOperationBaseScreen(OperationBaseScreen, OperationActionBindings, AbstractClassMessagePump):
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
        self,
        weight_threshold_input: WeightThresholdInput,
        account_auths_input: AccountAuthsInput,
        key_auths_input: KeyAuthsInput,
    ) -> Authority | None:
        if weight_threshold_input.value:
            return Authority(
                weight_threshold=weight_threshold_input.value,
                account_auths=self._split_auths_fields(account_auths_input.value),
                key_auths=self._split_auths_fields(key_auths_input.value),
            )
        return None
