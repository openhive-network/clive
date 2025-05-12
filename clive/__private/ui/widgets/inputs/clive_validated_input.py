from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from textual import on
from textual.containers import Vertical
from textual.widgets import Pretty

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core.formatters.humanize import humanize_validation_result
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from rich.highlighter import Highlighter
    from textual.app import ComposeResult
    from textual.suggester import Suggester
    from textual.validation import ValidationResult, Validator
    from textual.widgets._input import InputType, InputValidationOn


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
        message = f"""\
Input validation failed{additional}. Reasons:
{humanize_validation_result(validation_result)}"""
        super().__init__(message)


class FailedManyValidationError(CliveValidatedInputError):
    """Raised when validation of many `CliveValidatedInput` fails."""

    def __init__(self, errors: list[InputValueError | FailedValidationError]) -> None:
        self.errors = errors
        message = self._create_error_message(errors)
        super().__init__(message)

    def _create_error_message(self, errors: list[InputValueError | FailedValidationError]) -> str:
        message = "Input validation failed for:\n"
        for error in errors:
            message += f"- `{error.input_name}`"
            if isinstance(error, InputValueError):
                message += f" Reason:\n{error.reason}"
            elif isinstance(error, FailedValidationError):
                message += f" Reasons:\n{error.validation_result.failure_descriptions}"
            message += "\n"

        return message.strip()  # remove the last \n


class InputValueError(CliveValidatedInputError):
    """Raised when cannot get the value of the `CliveValidatedInput`."""

    def __init__(self, reason: str, *, input_name: str | None = None) -> None:
        self.reason = reason
        self.input_name = input_name
        additional = self._get_input_name_details(input_name)
        message = f"""\
Input value error{additional}. Reason:
{reason}"""
        super().__init__(message)


class CliveValidatedInput[InputReturnT](CliveWidget, AbstractClassMessagePump):
    """A custom input that shows a title and failed validation reasons (if any). For more look into `CliveInput`."""

    DEFAULT_CSS = """
    CliveValidatedInput {
        width: 1fr;
        height: auto;

        Vertical {
            height: auto;
        }

        Pretty {
            padding: 0 1; /* workaround for a bug in textual with margins */
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

    def make_required(self, message: str = CliveInput.DEFAULT_REQUIRED_FAILURE_DESCRIPTION) -> None:
        self.input.make_required(message)

    def make_optional(self) -> None:
        self.input.make_optional()

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

        Raises:  # noqa: D406
        ------
        FailedValidationError: Raised when validation fails.
        InputValueError: Raised when cannot get the value of the input.
        """
        self.validate_with_error(treat_as_required=False)
        return self._value

    @property
    def is_empty(self) -> bool:
        return self.input.is_empty

    def load_new_suggestions(self, suggestions: list[str]) -> None:
        self.input.load_new_suggestions(suggestions)

    def value_or_none(
        self,
        *,
        notify_on_value_error: bool = True,
        notify_on_validation_error: bool = False,
    ) -> InputReturnT | None:
        """
        Return the value of the input as given InputReturnT or None if validation fails.

        Args:
        ----
        notify_on_value_error: Whether to show a notification when the input value is invalid.
            True by default since this error won't be visible in the UI otherwise.
        notify_on_validation_error: Whether to show a notification when the input validation fails.
            False by default since the validation error will be visible in the UI, under the input.
        """
        try:
            self.validate_with_error(treat_as_required=False)
        except (InputValueError, FailedValidationError) as error:
            if isinstance(error, InputValueError) and not notify_on_value_error:
                return None
            if isinstance(error, FailedValidationError) and not notify_on_validation_error:
                return None
            self.app.notify(str(error), severity="error")
            return None
        return self._value

    def validate_with_error(self, *, treat_as_required: bool = True) -> None:
        """
        Validate the input and raise an exception if validation fails.

        Raises:  # noqa: D406
        ------
        FailedValidationError: Raised when validation fails.
        InputValueError: Raised when cannot get the value of the input due to an error, which validation doesn't catch.
        """

        def try_get_value() -> None:
            try:
                _ = self._value  # Error might be raised when creating InputReturnT
            except Exception as error:
                raise InputValueError(str(error), input_name=self.input.title) from error

        validation_result = self.input.validate(self.value_raw, treat_as_required=treat_as_required)

        if validation_result is None:
            # Means no validators were defined for the input.
            try_get_value()
            return

        if not validation_result.is_valid:
            raise FailedValidationError(validation_result, input_name=self.input.title)

        try_get_value()

    def validate_passed(
        self,
        *,
        treat_as_required: bool = True,
        notify_on_value_error: bool = True,
        notify_on_validation_error: bool = False,
    ) -> bool:
        """
        Validate the input and return True if validation passes, False otherwise.

        Args:
        ----
        treat_as_required: Whether to treat the input as required when validating.
            Even if the input is not required, it will be validated as if it was.
        notify_on_value_error: Whether to show a notification when the input value is invalid.
            True by default since this error won't be visible in the UI otherwise.
        notify_on_validation_error: Whether to show a notification when the input validation fails.
            False by default since the validation error will be visible in the UI, under the input.
        """
        try:
            self.validate_with_error(treat_as_required=treat_as_required)
        except (InputValueError, FailedValidationError) as error:
            if isinstance(error, InputValueError) and not notify_on_value_error:
                return False
            if isinstance(error, FailedValidationError) and not notify_on_validation_error:
                return False
            self.app.notify(str(error), severity="error")
            return False
        return True

    @classmethod
    def validate_many(
        cls,
        *inputs: CliveValidatedInput[Any],
        treat_as_required: bool = True,
        notify_on_value_error: bool = True,
        notify_on_validation_error: bool = False,
    ) -> bool:
        """
        Validate many inputs and return True if all of them are valid, False otherwise.

        For more info look into `validate_passed`.
        """
        results: list[bool] = [
            input_obj.validate_passed(
                treat_as_required=treat_as_required,
                notify_on_value_error=notify_on_value_error,
                notify_on_validation_error=notify_on_validation_error,
            )
            for input_obj in inputs
        ]
        # Couldn't use `all` right away because we want to validate all inputs, and `all` stops at the first False.
        return all(results)

    @classmethod
    def validate_many_with_error(cls, *inputs: CliveValidatedInput[Any]) -> None:
        """
        Validate many inputs and raise an exception if any of them is invalid.

        Raises:  # noqa: D406
        ------
        FailedManyValidationError: Raised when validation fails.
        """
        combined_errors: list[FailedValidationError | InputValueError] = []
        for input_obj in inputs:
            try:
                input_obj.validate_with_error()
            except (FailedValidationError, InputValueError) as error:
                combined_errors.append(error)

        if combined_errors:
            raise FailedManyValidationError(combined_errors)

    def clear_validation(self, *, clear_value: bool = True) -> None:
        """Clear the validation of the input."""
        self.input.clear_validation(clear_value=clear_value)

    @on(CliveInput.Validated)
    def _show_invalid_reasons(self, event: CliveInput.Validated) -> None:
        # Updating the UI to show the reasons why validation failed
        validation_result = event.result
        if validation_result is None:
            # restore to the unchanged state
            self.pretty.update([])
            self.pretty.display = False
            return

        if validation_result.is_valid:
            self.pretty.display = False
        else:
            self.pretty.update(validation_result.failure_descriptions)
            self.pretty.display = True
