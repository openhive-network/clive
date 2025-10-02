from __future__ import annotations

from textual.validation import Function, ValidationResult, Validator

from clive.__private.models.asset import Asset


class AssetAmountValidator(Validator):
    def __init__(self, asset_type: type[Asset.AnyT]) -> None:
        super().__init__()

        self.asset_type = asset_type

    def validate(self, value: str) -> ValidationResult:
        invalid_precision_message = (
            f"Invalid precision for {self._get_asset_name()}. Must be <={self._get_asset_precision()}."
        )
        validators = [
            Function(self._validate_precision, invalid_precision_message),
        ]

        return ValidationResult.merge([validator.validate(value) for validator in validators])

    def _validate_precision(self, value: str) -> bool:
        return self._get_given_precision(value) <= self._get_asset_precision()

    def _get_asset_precision(self) -> int:
        return Asset.get_precision(self.asset_type)

    def _get_asset_name(self) -> str:
        return Asset.get_symbol(self.asset_type)

    def _get_given_precision(self, value: str) -> int:
        if "." not in value:
            return 0
        return len(value.split(".")[1])
