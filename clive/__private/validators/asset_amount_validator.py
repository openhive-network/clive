from __future__ import annotations

from typing import TYPE_CHECKING

from textual.validation import Function, ValidationResult, Validator

if TYPE_CHECKING:
    from clive.models import Asset


class AssetAmountValidator(Validator):
    def __init__(self, asset_type: type[Asset.AnyT]) -> None:
        super().__init__()

        self.asset_type = asset_type

    def validate(self, value: str) -> ValidationResult:
        result = self.success()

        invalid_precision_message = (
            f"Invalid precision for {self._get_asset_name()}. Must be <={self._get_asset_precision()}."
        )
        validators = [
            Function(self._validate_precision, invalid_precision_message),
        ]

        return result.merge([validator.validate(value) for validator in validators])

    def _validate_precision(self, value: str) -> bool:
        return self._get_given_precision(value) <= self._get_asset_precision()

    def _get_asset_precision(self) -> int:
        return self.asset_type.get_asset_information().precision

    def _get_asset_name(self) -> str:
        return self.asset_type.get_asset_information().symbol[0]

    def _get_given_precision(self, value: str) -> int:
        if "." not in value:
            return 0
        return len(value.split(".")[1])
