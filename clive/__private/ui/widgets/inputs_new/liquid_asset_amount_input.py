from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.containers import Horizontal, Vertical

from clive.__private.ui.widgets.currency_selector import CurrencySelectorLiquid
from clive.__private.ui.widgets.inputs_new.clive_validated_input import (
    CliveValidatedInput,
)
from clive.__private.ui.widgets.placeholders_constants import NUMERIC_PLACEHOLDER
from clive.__private.validators.asset_amount_validator import AssetAmountValidator
from clive.models import Asset

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.app import ComposeResult
    from textual.widgets._input import InputValidationOn


class LiquidAssetAmountInput(CliveValidatedInput[Asset.LiquidT]):
    """An input for a liquid asset (HBD/HIVE) amount."""

    DEFAULT_CSS = """
    LiquidAssetAmountInput {
      height: auto;

      Vertical {
        height: auto;

        Horizontal {
          height: auto;

          CliveInput {
            width: 1fr;
          }

          CurrencySelectorLiquid {
            width: 14;
          }
        }
      }
    }
    """

    def __init__(
        self,
        title: str = "Amount",
        value: str | float | None = None,
        placeholder: str = NUMERIC_PLACEHOLDER,
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
        self._currency_selector = CurrencySelectorLiquid()
        default_asset_type = self._currency_selector.default_asset_cls
        default_asset_precision = default_asset_type.get_asset_information().precision

        super().__init__(
            title=title,
            value=str(value) if value is not None else None,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            restrict=self._create_restriction(default_asset_precision),
            type="number",
            validators=[AssetAmountValidator(default_asset_type)],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @property
    def _value(self) -> Asset.LiquidT:
        """
        Return the value of the input as a liquid asset.

        Probably you want to use other `value_` properties instead.

        Raises
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return self._currency_selector.create_asset(self.value_raw)

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield self.input
                yield self._currency_selector
            yield self.pretty

    @on(CurrencySelectorLiquid.Changed)
    def _update_restrictions(self) -> None:
        selected_asset_type = self._currency_selector.asset_cls
        selected_asset_precision = selected_asset_type.get_asset_information().precision

        # update input restrict
        self.input.restrict = self._create_restriction(selected_asset_precision)

        # update asset amount validator
        self.input.validators = [
            validator for validator in self.input.validators if not isinstance(validator, AssetAmountValidator)
        ]
        self.input.validators.append(AssetAmountValidator(selected_asset_type))

        # need to revalidate the input (possible to switch from higher precision to lower precision)
        self.input.validate(self.input.value)

    def _create_restriction(self, precision: int) -> str:
        precision_digits = f"{{0,{precision}}}"
        return rf"\d*\.?\d{precision_digits}"
