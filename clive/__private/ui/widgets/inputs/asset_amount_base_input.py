from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, cast

from textual import on
from textual.containers import Horizontal, Vertical

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.models import Asset
from clive.__private.ui.widgets.currency_selector.currency_selector_base import CurrencySelectorBase
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    CliveValidatedInput,
)
from clive.__private.validators.asset_amount_validator import AssetAmountValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.app import ComposeResult
    from textual.widgets._input import InputValidationOn


class AssetAmountInput[AssetInputT: (Asset.VotingT, Asset.LiquidT, Asset.Hive)](
    CliveValidatedInput[AssetInputT], AbstractClassMessagePump
):
    """
    Base input for all asset types.

    Attributes:
        DEFAULT_CSS: Default CSS for the asset amount input.

    Args:
        title: The title of the input.
        value: The initial value of the input.
        placeholder: Placeholder text for the input. If not set, it is dynamically generated based on the asset type.
        always_show_title: Whether to always show the title (by default it is shown only when focused).
        include_title_in_placeholder_when_blurred: Whether to include the title in the placeholder when blurred.
        show_invalid_reasons: Whether to show reasons for invalid input.
        required: Whether the input is required.
        validate_on: When to validate the input.
        valid_empty: Whether an empty input is considered as valid.
        id: The ID of the input in the DOM.
        classes: The CSS classes for the input.
        disabled: Whether the input is disabled.
    """

    DEFAULT_CSS = """
    AssetAmountInput {
      height: auto;

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
        with self.prevent(CurrencySelectorBase.Changed):
            self._currency_selector: CurrencySelectorBase = self.create_currency_selector()
        default_asset_precision = Asset.get_precision(self.default_asset_type)

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
            validators=[AssetAmountValidator(self.default_asset_type)],
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

        Raises:  # noqa: D406
            AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return cast("AssetInputT", self._currency_selector.create_asset(self.value_raw))

    @property
    def default_asset_type(self) -> type[AssetInputT]:
        return self._currency_selector.default_asset_cls

    @property
    def selected_asset_type(self) -> type[AssetInputT]:
        return self._currency_selector.asset_cls

    @property
    def selected_asset_precision(self) -> int:
        return Asset.get_precision(self.selected_asset_type)

    def select_asset(self, asset_type: type[AssetInputT]) -> None:
        with self.prevent(CurrencySelectorBase.Changed):
            self._currency_selector.select_asset(asset_type)

    def disable_currency_selector(self) -> None:
        self._currency_selector.disabled = True

    def enable_currency_selector(self) -> None:
        self._currency_selector.disabled = False

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
            self.input.placeholder = self._get_dynamic_placeholder(self.selected_asset_precision)

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
    def create_currency_selector(self) -> CurrencySelectorBase:
        pass
