from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from textual import on
from textual.containers import Vertical
from textual.widgets import Pretty

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs_new.clive_input import CliveInput
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from rich.highlighter import Highlighter
    from textual.app import ComposeResult
    from textual.suggester import Suggester
    from textual.validation import ValidationResult, Validator
    from textual.widgets._input import InputType, InputValidationOn


InputReturnT = TypeVar("InputReturnT")


class CliveValidatedInputError(CliveError):
    """Base class for all errors related to `CliveValidatedInput`."""

    @staticmethod
    def _get_input_name_details(input_name: str | None) -> str:
        return f" for `{input_name}`" if input_name else ""


class FailedValidationError(CliveValidatedInputError):
    """Raised when validation of `CliveValidatedInput`  fails."""

    def __init__(self, validation_result: ValidationResult, *, input_name: str | None = None) -> None:
        self.validation_result = validation_result
        self.input_name = input_name
        additional = self._get_input_name_details(input_name)
        self.message = f"""\
Input validation failed{additional}. Reasons:
{validation_result.failure_descriptions}"""
        super().__init__(self.message)


class InputValueError(CliveValidatedInputError):
    """Raised when cannot get the value of the `CliveValidatedInput`."""

    def __init__(self, reason: str, *, input_name: str | None = None) -> None:
        self.reason = reason
        self.input_name = input_name
        additional = self._get_input_name_details(input_name)
        self.message = f"""\
Input value error{additional}. Reason:
{reason}"""
        super().__init__(self.message)


class CliveValidatedInput(CliveWidget, Generic[InputReturnT], AbstractClassMessagePump):
    """A custom input that shows a title and failed validation reasons (if any). For more look into `CliveInput`."""

    DEFAULT_CSS = """
    CliveValidatedInput {
        height: auto;

        Vertical {
            height: auto;
        }
    }
    """

    def __init__(
        self,
        title: str,
        value: str | None = None,
        placeholder: str = "",
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = True,
        password: bool = False,
        restrict: str | None = None,
        type: InputType = "text",  # noqa: A002
        max_length: int = 0,
        highlighter: Highlighter | None = None,
        suggester: Suggester | None = None,
        validators: Validator | Iterable[Validator] | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """
        Initialise the widget.

        New args (compared to `CliveInput`):
        ------------------------------------
        show_invalid_reasons: Whether to show the reasons why validation failed.
        """
        super().__init__(id=id, classes=classes, disabled=disabled)
        self.input = CliveInput(
            title=title,
            value=value,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            required=required,
            password=password,
            restrict=restrict,
            type=type,
            max_length=max_length,
            highlighter=highlighter,
            suggester=suggester,
            validators=validators,
            validate_on=validate_on,
            valid_empty=valid_empty,
        )
        self._should_show_invalid_reasons = show_invalid_reasons
        self.pretty = Pretty([])
        self.pretty.display = False

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.input
            yield self.pretty

    @property
    @abstractmethod
    def _value(self) -> InputReturnT:
        """
        Return the value of the input as given InputReturnT type.

        Probably you want to use other `value_` properties instead.
        """

    @property
    def value_raw(self) -> str:
        """Return the raw value of the input."""
        return self.input.value

    @property
    def value_or_error(self) -> InputReturnT:
        """
        Return the validated value of the input as given InputReturnT or raise an exception if validation fails.

        Raises
        ------
        FailedCliveInputValidationError: Raised when validation fails.
        CliveInputValueError: Raised when cannot get the value of the input.
        """
        self.validate_with_error(treat_as_required=False)
        return self._value

    @property
    def value_or_none(self) -> InputReturnT | None:
        """Return the value of the input as given InputReturnT or None if validation fails."""
        try:
            self.validate_with_error(treat_as_required=False)
        except CliveValidatedInputError:
            return None
        return self._value

    @property
    def value_or_notification(self) -> InputReturnT | None:
        """Return the value of the input as given InputReturnT or None and raise a Notification if validation fails."""
        try:
            self.validate_with_error(treat_as_required=False)
        except CliveValidatedInputError as error:
            self.app.notify(str(error), severity="error")
            return None
        return self._value

    def validate_with_error(self, *, treat_as_required: bool = True) -> None:
        """
        Validate the input and raise an exception if validation fails.

        Raises
        ------
        InputValidationError: Raised when validation fails.
        InputValueError: Raised when cannot get the value of the input due to an error, which validation doesn't catch.
        """

        def try_get_value() -> None:
            try:
                _ = self._value  # Error might be raised when creating InputReturnT
            except Exception as error:  # noqa: BLE001
                raise InputValueError(str(error), input_name=self.input.title) from error

        validation_result = self.input.validate(self.value_raw, treat_as_required=treat_as_required)

        if validation_result is None:
            # Means no validators were defined for the input.
            try_get_value()
            return

        if not validation_result.is_valid:
            raise FailedValidationError(validation_result, input_name=self.input.title)

        try_get_value()

    def validate_with_notification(self, *, treat_as_required: bool = True) -> bool:
        """Validate the input and raise a Notification if validation fails."""
        try:
            self.validate_with_error(treat_as_required=treat_as_required)
        except CliveValidatedInputError as error:
            self.app.notify(str(error), severity="error")
            return False
        return True

    @on(CliveInput.Validated)
    def _show_invalid_reasons(self, event: CliveInput.Validated) -> None:
        # Updating the UI to show the reasons why validation failed
        validation_result = event.result
        if validation_result is None:
            return

        if validation_result.is_valid:
            self.pretty.display = False
        else:
            self.query_one(Pretty).update(validation_result.failure_descriptions)
            self.pretty.display = True
