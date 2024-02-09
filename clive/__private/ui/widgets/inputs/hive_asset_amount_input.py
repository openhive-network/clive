from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.inputs.liquid_asset_amount_input import LiquidAssetAmountInput
from clive.models import Asset

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.widgets._input import InputValidationOn


class HiveAssetAmountInput(LiquidAssetAmountInput):
    """An input for asset HIVE amount."""

    def __init__(
        self,
        title: str = "Amount",
        value: str | float | None = None,
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            title=title,
            value=value,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

        symbol = Asset.Hive.get_asset_information().symbol[0]
        self._currency_selector.value = self._currency_selector.get_selectable(symbol)
        self._currency_selector.prompt = symbol
        self._currency_selector.disabled = True

    @property
    def _value(self) -> Asset.Hive:
        """
        Return the value of the input as a HIVE asset.

        Probably you want to use other `value_` properties instead.

        Raises
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return super()._value  # type: ignore[return-value] # we re sure it is Hive

    @property
    def selected_asset_type(self) -> type[Asset.Hive]:
        return super().selected_asset_type  # type: ignore[return-value] # we re sure it is Hive
