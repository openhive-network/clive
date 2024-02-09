from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal, Vertical

from clive.__private.ui.widgets.currency_selector.currency_selector_hive import CurrencySelectorHive
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    CliveValidatedInput,
)
from clive.__private.validators.asset_amount_validator import AssetAmountValidator
from clive.models import Asset

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.app import ComposeResult
    from textual.widgets._input import InputValidationOn


class HiveAssetAmountInput(CliveValidatedInput[Asset.Hive]):
    """An input for asset HIVE amount."""

    DEFAULT_CSS = """
    HiveAssetAmountInput {
      height: auto;

      Vertical {
        height: auto;

        Horizontal {
          height: auto;

          CliveInput {
            width: 1fr;
          }

          CurrencySelectorHive {
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
        placeholder: str | None = None,
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
        """
        Initialize the widget.

        Args difference from `CliveValidatedInput`:
        ----
        placeholder: If not provided, placeholder will be dynamically generated based on the asset type.
        """
        self._currency_selector = CurrencySelectorHive()
        asset_precision = Asset.Hive.get_asset_information().precision

        self._currency_selector.disabled = True
        # As HIVE is always the only choice, we do not want to allow the user to roll down the selector.

        super().__init__(
            title=title,
            value=str(value) if value is not None else None,
            placeholder=self._get_dynamic_placeholder(asset_precision),
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            restrict=self._create_restriction(asset_precision),
            type="number",
            validators=[AssetAmountValidator(Asset.Hive)],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

        self._dynamic_placeholder = placeholder is None

    @property
    def _value(self) -> Asset.Hive:
        """
        Return the value of the input as a HIVE asset.

        Probably you want to use other `value_` properties instead.

        Raises
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return self._currency_selector.create_asset(self.value_raw)

    @property
    def selected_asset_type(self) -> type[Asset.Hive]:
        return self._currency_selector.asset_cls

    @property
    def selected_asset_precision(self) -> int:
        return self.selected_asset_type.get_asset_information().precision

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield self.input
                yield self._currency_selector
            yield self.pretty

    def _create_restriction(self, precision: int) -> str:
        precision_digits = f"{{0,{precision}}}"
        return rf"\d*\.?\d{precision_digits}"

    def _get_dynamic_placeholder(self, precision: int) -> str:
        max_allowed_precision = 9
        assert precision >= 0, f"Precision must be non-negative, got {precision}"
        assert precision <= max_allowed_precision, f"Precision must be at most {max_allowed_precision}, got {precision}"
        numbers = "123456789"
        return f"e.g.: 1.{numbers[:precision]}"
