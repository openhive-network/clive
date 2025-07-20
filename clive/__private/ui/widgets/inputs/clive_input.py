from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Literal

from textual import on, validation
from textual.binding import Binding
from textual.events import Blur, Focus
from textual.message import Message
from textual.reactive import var
from textual.validation import ValidationResult, Validator
from textual.widgets import Input

from clive.__private.ui.clive_suggester import CliveSuggester

if TYPE_CHECKING:
    from collections.abc import Iterable

    from rich.highlighter import Highlighter
    from textual.suggester import Suggester
    from textual.widgets._input import InputType, InputValidationOn


class CliveInput(Input):
    """
    A custom input that shows a title on the border top-left corner.

    Attributes:
        DEFAULT_CSS: Default CSS for the CliveInput.
        BINDINGS: Key bindings for the CliveInput.
        DEFAULT_REQUIRED_FAILURE_DESCRIPTION: Default description for required failure.
        title: The title of the input.
        required: Whether the input is required.
        required_failure_description: The description to show when the input is required but empty.
        always_show_title: Whether to always show the title (by default it is shown only when focused).

    Args:
        title: The title of the input.
        value: The initial value of the input.
        placeholder: Placeholder text for the input.
        always_show_title: Whether to always show the title (by default it is shown only when focused).
        include_title_in_placeholder_when_blurred: Whether to include the title in the placeholder when blurred.
        required: Whether the input is required.
        password: Whether the input is a password field.
        restrict: Regular expression to restrict input to a specific format .
        type: The type of input.
        max_length: Maximum length of the input value.
        highlighter: Highlighter for syntax highlighting.
        suggester: Suggester for auto-completion.
        validators: Validators for the input.
        validate_on: When to validate the input.
        valid_empty: Whether an empty input is considered as valid.
        name: Name attribute for the input.
        id: The ID of the input in the DOM.
        classes: The CSS classes for the input.
        disabled: Whether the input is disabled.
    """

    DEFAULT_CSS = """
    $regular-color: $primary;
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
    BINDINGS = [
        Binding("up", "suggest_next", "Suggest next", show=False),
        Binding("down", "suggest_previous", "Suggest previous", show=False),
    ]

    DEFAULT_REQUIRED_FAILURE_DESCRIPTION: Final[str] = "This field is required"

    _DEFAULT_VALIDATE_ON: Final[set[Literal[InputValidationOn]]] = {"submitted", "changed"}
    """To avoid validation while focusing other element (without filling input),
    more details: https://github.com/Textualize/textual/issues/5130"""

    title: str = var("", init=False)  # type: ignore[assignment]
    required: bool = var(default=False, init=False)  # type: ignore[assignment]
    required_failure_description: str = var(DEFAULT_REQUIRED_FAILURE_DESCRIPTION, init=False)  # type: ignore[assignment]
    always_show_title: bool = var(default=False, init=False)  # type: ignore[assignment]

    @dataclass
    class Validated(Message):
        value: str
        result: ValidationResult | None = None

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
        super().__init__(
            value=value,
            placeholder=placeholder,
            password=password,
            restrict=restrict,
            type=type,
            max_length=max_length,
            highlighter=highlighter,
            suggester=suggester if suggester else CliveSuggester(),
            validators=validators,
            validate_on=validate_on if validate_on is not None else self._DEFAULT_VALIDATE_ON,
            valid_empty=valid_empty,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.set_reactive(self.__class__.required, required)  # type: ignore[arg-type]
        self.set_reactive(self.__class__.always_show_title, always_show_title)  # type: ignore[arg-type]
        self.set_reactive(self.__class__.title, title)  # type: ignore[arg-type]
        self._include_title_in_placeholder_when_blurred = include_title_in_placeholder_when_blurred
        self._unmodified_placeholder = placeholder

        self._configure()

    @property
    def unmodified_placeholder(self) -> str:
        return self._unmodified_placeholder

    @property
    def has_suggestion(self) -> bool:
        return bool(self._suggestion)

    @property
    def is_empty(self) -> bool:
        return not bool(self.value)

    async def action_suggest_next(self) -> None:
        await self._suggest(mode="next")

    async def action_suggest_previous(self) -> None:
        await self._suggest(mode="previous")

    def add_suggestion(self, *suggestions: str) -> None:
        assert isinstance(self.suggester, CliveSuggester), (
            "In order to add new suggestions you have to use CliveSuggester."
        )
        self.suggester.add_suggestion(*suggestions)

    def clear_suggestions(self) -> None:
        if self.suggester:
            assert isinstance(self.suggester, CliveSuggester), (
                "In order to clear suggestions you have to use CliveSuggester."
            )
            self.suggester.clear_suggestions()

    def make_required(self, message: str = DEFAULT_REQUIRED_FAILURE_DESCRIPTION) -> None:
        self.set_reactive(self.__class__.required_failure_description, message)  # type: ignore[arg-type]
        self.required = True

    def make_optional(self) -> None:
        self.required = False

    def set_style(self, mode: Literal["initial", "valid", "invalid"]) -> None:
        valid_class = "-valid"
        invalid_class = "-invalid"

        if mode == "initial":
            self.remove_class(valid_class, invalid_class)
            return

        valid = mode == "valid"

        self.add_class(valid_class if valid else invalid_class)
        self.remove_class(invalid_class if valid else valid_class)

    def validate(self, value: str, *, treat_as_required: bool = False) -> ValidationResult | None:
        """
        Validate the value of the input.

        Args:
            value: The value to validate.
            treat_as_required: If True, treat the input as required even if it is not.

        Returns:
            The result of the validation.
        """
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
        return (
            bool(self.title)
            and self._include_title_in_placeholder_when_blurred
            and not self.always_show_title
            and not self.has_focus
        )

    def _configure(self) -> None:
        if self.required:
            self._add_length_validator()

        self._update_border_title_with_current_sate()
        self._update_placeholder_with_current_state()

    def _validate_placeholder(self, placeholder: str) -> str:
        self._unmodified_placeholder = placeholder
        return self._determine_placeholder()

    def _watch_required_failure_description(self) -> None:
        self._remove_length_validators()
        self._add_length_validator()

    def _watch_always_show_title(self) -> None:
        self._update_border_title_with_current_sate()
        self._update_placeholder_with_current_state()

    def _watch_title(self) -> None:
        self._update_border_title_with_current_sate()
        self._update_placeholder_with_current_state()

    def _watch_required(self, required: bool) -> None:  # noqa: FBT001
        self._update_border_title_with_current_sate()
        self._remove_length_validators()

        if not required:
            self.clear_validation()
            return

        self._add_length_validator()

    def _watch_value(self, value: str) -> None:
        # Textual does not update the cursor position when the value changes dynamically, so we place the cursor
        # all the way to the right
        self.action_end()

        # value can be set programmatically, so we need to update the border title accordingly
        if self.always_show_title:
            return super()._watch_value(value)

        self._update_border_title_with_current_sate()
        return super()._watch_value(value)

    @on(Focus)
    def _show_border_title(self) -> None:
        self.has_focus = True

        if self.always_show_title:
            return

        self.border_title = self._get_title_with_required()
        self.placeholder = self._unmodified_placeholder

    @on(Blur)
    def _hide_border_title(self) -> None:
        self.has_focus = False

        if self.always_show_title:
            return

        if not self.value:
            # If the input is empty, we want to show the required symbol only in the border title.
            # If there is a value, title will be included in the border title. (see _show_border_title)
            # So when there is value, the user can still see the title.
            self.border_title = self._get_required_symbol()

        self._update_placeholder_with_current_state()

    def _remove_length_validators(self) -> None:
        for validator in self.validators:
            if isinstance(validator, validation.Length):
                self.validators.remove(validator)

    def _add_length_validator(self) -> None:
        self.validators.append(validation.Length(minimum=1, failure_description=self.required_failure_description))

    def _update_border_title_with_current_sate(self) -> None:
        self.border_title = self._determine_border_title()

    def _update_placeholder_with_current_state(self) -> None:
        self.set_reactive(self.__class__.placeholder, self._determine_placeholder())

    def _determine_placeholder(self) -> str:
        if self._should_include_title_in_placeholder:
            return self._get_modified_placeholder()
        return self._unmodified_placeholder

    def _determine_border_title(self) -> str:
        if self.always_show_title or self.value or self.has_focus:
            return self._get_title_with_required()
        return self._get_required_symbol()

    def _get_modified_placeholder(self) -> str:
        return f"{self.title} {self._unmodified_placeholder}".strip()

    def _get_required_symbol(self) -> str:
        return "*" if self.required else ""

    def _get_title_with_required(self) -> str:
        prefix = self._get_required_symbol()
        return f"{prefix} {self.title}".strip()

    async def _suggest(self, mode: Literal["next", "previous"]) -> None:
        suggester = self.suggester
        if not isinstance(suggester, CliveSuggester) or self.is_empty:
            return

        suggester.next_selection() if mode == "next" else suggester.previous_selection()
        self.run_worker(suggester._get_suggestion(self, self.value))
