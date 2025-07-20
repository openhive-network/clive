from __future__ import annotations

from clive.__private.ui.widgets.inputs.text_input import TextInput


class LabelizedInput(TextInput):
    """
    An input that cannot be edited. It is used to display a static value with same style as other inputs.

    Args:
        title: The title of the input.
        value: The value to display in the input.
        id: The ID of the input widget.
        classes: Additional CSS classes for the input.
    """

    def __init__(
        self,
        title: str,
        value: str,
        *,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(
            title=title,
            value=value,
            always_show_title=True,
            include_title_in_placeholder_when_blurred=False,
            show_invalid_reasons=False,
            required=False,
            validate_on=[],
            id=id,
            classes=classes,
            disabled=True,
        )

    def clear_validation(self) -> None:  # type: ignore[override]
        """Clear the validation of the input."""
        # Cannot clear the value of a labelized input
        self.input.clear_validation(clear_value=False)
