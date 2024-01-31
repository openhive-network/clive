from __future__ import annotations

from clive.__private.ui.widgets.inputs.text_input import TextInput


class LabelizedInput(TextInput):
    """An input that cannot be edited. It is used to display a static value with same style as other inputs."""

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
