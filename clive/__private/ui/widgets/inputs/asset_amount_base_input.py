from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from textual import on
from textual.containers import Horizontal, Vertical

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.currency_selector.currency_selector_base import CurrencySelectorBase
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    CliveValidatedInput,
)
from clive.__private.validators.asset_amount_validator import AssetAmountValidator
from clive.models import Asset

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.app import ComposeResult
    from textual.widgets._input import InputValidationOn

AssetInputT = TypeVar("AssetInputT", Asset.VotingT, Asset.LiquidT)


class AssetAmountInput(CliveValidatedInput[AssetInputT], Generic[AssetInputT], AbstractClassMessagePump):
    """Base input for all asset types."""

    DEFAULT_CSS = """
    AssetAmountInput {
      height: auto;
      width: 1fr;

      Vertical {
        height: auto;

        Horizontal {
          height: auto;

          CliveInput {
            width: 1fr;
          }

          CurrencySelectorBase {
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
        self._currency_selector: CurrencySelectorBase[AssetInputT] = self.create_currency_selector()
        default_asset_type = self._currency_selector.default_asset_cls
        default_asset_precision = default_asset_type.get_asset_information().precision

        super().__init__(
            title=title,
            value=str(value) if value is not None else None,
            placeholder=self._get_dynamic_placeholder(default_asset_precision),
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

        self._dynamic_placeholder = placeholder is None

    @property
    def _value(self) -> AssetInputT:
        """
        Return the value of the input as a liquid asset.

        Probably you want to use other `value_` properties instead.

        Raises
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return self._currency_selector.create_asset(self.value_raw)

    @property
    def selected_asset_type(self) -> type[AssetInputT]:
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

    @on(CurrencySelectorBase.Changed)
    def _asset_changed(self) -> None:
        # update placeholder
        if self._dynamic_placeholder:
            self.input.set_unmodified_placeholder(self._get_dynamic_placeholder(self.selected_asset_precision))

        # update input restrict
        self.input.restrict = self._create_restriction(self.selected_asset_precision)

        # update asset amount validator
        self.input.validators = [
            validator for validator in self.input.validators if not isinstance(validator, AssetAmountValidator)
        ]
        self.input.validators.append(AssetAmountValidator(self.selected_asset_type))

        # need to revalidate the input (possible to switch from higher precision to lower precision)
        self.input.validate(self.input.value)

    def _create_restriction(self, precision: int) -> str:
        precision_digits = f"{{0,{precision}}}"
        return rf"\d*\.?\d{precision_digits}"

    def _get_dynamic_placeholder(self, precision: int) -> str:
        max_allowed_precision = 9
        assert precision >= 0, f"Precision must be non-negative, got {precision}"
        assert precision <= max_allowed_precision, f"Precision must be at most {max_allowed_precision}, got {precision}"
        numbers = "123456789"
        return f"e.g.: 1.{numbers[:precision]}"

    @abstractmethod
    def create_currency_selector(self) -> CurrencySelectorBase[AssetInputT]:
        pass
