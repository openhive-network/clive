from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Vertical
from textual.events import Mount

from clive.__private.core.constants.tui.placeholders import MEMO_PLACEHOLDER
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.validators.private_key_in_memo_validator import PrivateKeyInMemoValidator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.app import ComposeResult
    from textual.suggester import Suggester
    from textual.validation import Validator
    from textual.widgets._input import InputValidationOn


class MemoInput(TextInput):
    """
    An input for a Hive memo.

    Attributes:
        DEFAULT_CSS: Default CSS for the memo input.
    """

    _ENCRYPTED_MEMO_CLASS: Final[str] = "-encrypted-memo"

    DEFAULT_CSS = """
    MemoInput {
        height: auto;

        Vertical {
            height: auto;

            CliveInput {
                width: 1fr;

                &.-encrypted-memo {
                    border-subtitle-background: $secondary;
                }
            }
        }
    }
    """

    def __init__(
        self,
        title: str = "Memo",
        value: str | None = None,
        placeholder: str = MEMO_PLACEHOLDER,
        *,
        always_show_title: bool = False,
        include_title_in_placeholder_when_blurred: bool = True,
        show_invalid_reasons: bool = True,
        required: bool = False,
        suggester: Suggester | None = None,
        validators: Validator | Iterable[Validator] | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            title=title,
            value=value,
            placeholder=placeholder,
            always_show_title=always_show_title,
            include_title_in_placeholder_when_blurred=include_title_in_placeholder_when_blurred,
            show_invalid_reasons=show_invalid_reasons,
            required=required,
            suggester=suggester,
            validators=validators or [PrivateKeyInMemoValidator(self.world)],
            validate_on=validate_on,
            valid_empty=valid_empty,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.input
            yield self.pretty

    @on(Mount)
    def _watch_input_value_change(self) -> None:
        self.watch(self.input, "value", self._update_encryption_status)

    def _update_encryption_status(self) -> None:
        if self.value_raw.startswith("#"):
            self.input.border_subtitle = "will be encrypted"
            self.input.add_class(self._ENCRYPTED_MEMO_CLASS)
        else:
            self.input.border_subtitle = None
            self.input.remove_class(self._ENCRYPTED_MEMO_CLASS)
        self.input.refresh()
