from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from textual import on, validation
from textual.events import Blur, Focus
from textual.message import Message
from textual.reactive import var
from textual.validation import ValidationResult, Validator
from textual.widgets import Input

if TYPE_CHECKING:
    from collections.abc import Iterable

    from rich.highlighter import Highlighter
    from textual.suggester import Suggester
    from textual.widgets._input import InputType, InputValidationOn


class CliveInput(Input):
    """A custom input that shows a title on the border top-left corner."""

    DEFAULT_CSS = """
    $regular-color: $accent
    $invalid-color: $error;
    $valid-color: $success-darken-3;

    CliveInput {
        border-title-background: $regular-color;
        border-title-color: $text;
        border-title-style: bold;
        border-subtitle-background: $regular-color;
        border-subtitle-color: $text;

        &.-valid {
            border-title-background: $valid-color;
            border-subtitle-background: $valid-color;
            border: tall $valid-color;
        }

        &.-invalid {
            border-title-background: $invalid-color;
            border-subtitle-background: $invalid-color;
            border: tall $invalid-color;
        }
    }
    """

    @dataclass
    class Validated(Message):
        value: str
        result: ValidationResult | None = None

    title: str = var("", init=False)  # type: ignore[assignment]

    def __init__(
        self,
        title: str,
        value: str | None = None,
        placeholder: str = "",
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
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
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """
        Initialise the widget.

        New args (compared to `Input`):
        -------------------------------
        title: The title to show on the border.
        always_show_title: Whether to always show the title on the border (by default it is shown only when focused).
        include_title_in_placeholder_when_blurred: Whether to include the title in the placeholder when not focused.
        required: Whether the input is required.
        """
        # Ensure we always end up with an Iterable of validators
        if isinstance(validators, Validator):
            _validators: list[Validator] = [validators]
        elif validators is None:
            _validators = []
        else:
            _validators = list(validators)

        if required:
            _validators = [*_validators, validation.Length(minimum=1, failure_description="This field is required")]

        self.set_reactive(self.__class__.title, title)  # type: ignore[arg-type]
        self.required = required
        self._always_show_title = always_show_title

        super().__init__(
            value=value,
            placeholder=placeholder,
            password=password,
            restrict=restrict,
            type=type,
            max_length=max_length,
            highlighter=highlighter,
            suggester=suggester,
            validators=_validators,
            validate_on=validate_on,
            valid_empty=valid_empty,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

        self._include_title_in_placeholder_when_blurred = include_title_in_placeholder_when_blurred

        self._unmodified_placeholder = placeholder

        self._configure()

    def set_unmodified_placeholder(self, placeholder: str) -> None:
        self._unmodified_placeholder = placeholder
        self.placeholder = self._get_placeholder()

    def _watch_title(self) -> None:
        self.border_title = self._determine_border_title()

    def validate(self, value: str, *, treat_as_required: bool = False) -> ValidationResult | None:
        """Validate the value of the input."""
        if not self.required and not value and not treat_as_required:
            return ValidationResult.success()

        result = super().validate(value)

        self.set_style(mode="valid" if self.is_valid else "invalid")
        self.post_message(self.Validated(value, result))
        return result

    def clear_validation(self, *, clear_value: bool = True) -> None:
        """Clear the validation of the input."""
        if clear_value:
            self.clear()
        self._valid = True
        self.set_style("initial")
        self.post_message(self.Validated("", None))

    @property
    def _should_include_title_in_placeholder(self) -> bool:
        return bool(self.title) and self._include_title_in_placeholder_when_blurred and not self._always_show_title

    def _configure(self) -> None:
        self.border_title = self._determine_border_title()
        self.placeholder = self._get_placeholder()

    def _determine_border_title(self) -> str:
        if self._always_show_title or self.value:
            return self._get_title_with_required()
        return self._get_required_symbol()

    def _get_required_symbol(self) -> str:
        return "*" if self.required else ""

    def _get_title_with_required(self) -> str:
        prefix = self._get_required_symbol()
        return f"{prefix} {self.title}".strip()

    def _get_modified_placeholder(self) -> str:
        return f"{self.title} {self._unmodified_placeholder}"

    def _get_placeholder(self) -> str:
        if self._should_include_title_in_placeholder:
            return self._get_modified_placeholder()
        return self._unmodified_placeholder

    @on(Focus)
    def _show_border_title(self) -> None:
        if self._always_show_title:
            return

        self.border_title = self._get_title_with_required()

        self.placeholder = self._unmodified_placeholder

    @on(Blur)
    def _hide_border_title(self) -> None:
        if self._always_show_title:
            return

        if not self.value:
            # If the input is empty, we want to show the required symbol only in the border title.
            # If there is a value, title will be included in the border title. (see _show_border_title)
            # So when there is value, the user can still see the title.
            self.border_title = self._get_required_symbol()

        self.placeholder = self._get_placeholder()

    def _watch_value(self, value: str) -> None:
        # value can be set programmatically, so we need to update the border title accordingly
        if self._always_show_title:
            return super()._watch_value(value)

        should_show_title = bool(value) or self.has_focus
        self.border_title = self._get_title_with_required() if should_show_title else self._get_required_symbol()
        return super()._watch_value(value)

    def set_style(self, mode: Literal["initial", "valid", "invalid"]) -> None:
        valid_class = "-valid"
        invalid_class = "-invalid"

        if mode == "initial":
            self.remove_class(valid_class, invalid_class)
            return

        valid = mode == "valid"

        self.add_class(valid_class if valid else invalid_class)
        self.remove_class(invalid_class if valid else valid_class)
