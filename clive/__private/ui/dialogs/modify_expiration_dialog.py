from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from textual.css.query import NoMatches
from textual.widgets import Label, Static

from clive.__private.core.formatters.data_labels import NOT_AVAILABLE_LABEL
from clive.__private.core.formatters.humanize import humanize_datetime, humanize_natural_time
from clive.__private.core.shorthand_timedelta import InvalidShorthandToTimedeltaError
from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.inputs.expiration_input import ExpirationInput
from clive.__private.validators.expiration_validator import ExpirationValidator

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.models.schemas import HiveDateTime


class ModifyExpirationDialog(CliveActionDialog["timedelta | datetime | None"]):
    DEFAULT_CSS = """
    ModifyExpirationDialog {
        CliveDialogContent {
            width: 60%;
        }

        #signed-warning {
            color: $warning;
            margin-bottom: 1;
        }

        #head-block-time {
            color: $text-muted;
        }

        #expiration-info {
            color: $text-muted;
        }

        #enter-description {
            margin-bottom: 1;
        }
    }
    """

    def __init__(
        self,
        expiration_value: timedelta | datetime,
        *,
        metadata_block_time: HiveDateTime | None = None,
        is_signed: bool = False,
    ) -> None:
        super().__init__(border_title="Modify this transaction expiration", confirm_button_label="Apply")
        self._expiration_value = expiration_value
        self._metadata_block_time = metadata_block_time
        self._is_signed = is_signed

    def _get_head_block_time(self) -> datetime | None:
        gdpo = self.node.cached.dynamic_global_properties_or_none
        if gdpo is None:
            return None
        return gdpo.time

    def _get_head_block_time_text(self) -> str:
        gdpo = self.node.cached.dynamic_global_properties_or_none
        if gdpo is None:
            return f"Head block time: {NOT_AVAILABLE_LABEL}"
        return f"Head block time: {humanize_datetime(gdpo.time)}"

    @staticmethod
    def _format_expiration_label(abs_time: datetime, remaining: timedelta) -> str:
        return f"Expiration: {humanize_datetime(abs_time)}, {humanize_natural_time(-remaining)}"

    def _get_expiration_info_text(self) -> str:
        gdpo = self.node.cached.dynamic_global_properties_or_none
        if gdpo is None:
            return f"Expiration: {NOT_AVAILABLE_LABEL}"

        expiration_value = self._expiration_value
        try:
            expiration_input = self.query_exactly_one("#expiration-delta-input", ExpirationInput)
            expiration_value = expiration_input._value
        except (NoMatches, ValueError, InvalidShorthandToTimedeltaError):
            pass

        if isinstance(expiration_value, datetime):
            abs_time = expiration_value.replace(tzinfo=UTC) if expiration_value.tzinfo is None else expiration_value
            return self._format_expiration_label(abs_time, abs_time - gdpo.time)

        if self._is_signed:
            ref = gdpo.time
        else:
            ref = self._metadata_block_time if self._metadata_block_time is not None else gdpo.time
        abs_time = ref + expiration_value
        return self._format_expiration_label(abs_time, abs_time - gdpo.time)

    def on_mount(self) -> None:
        self.set_interval(3, self._refresh_expiration_info)

    def _update_expiration_info_label(self) -> None:
        try:
            label = self.query_exactly_one("#expiration-info", DynamicLabel).query_one(Label)
        except NoMatches:
            return
        label.update(self._get_expiration_info_text())

    def _refresh_expiration_info(self) -> None:
        self._update_expiration_info_label()
        self._revalidate_input()

    def _revalidate_input(self) -> None:
        try:
            expiration_input = self.query_exactly_one("#expiration-delta-input", ExpirationInput)
        except NoMatches:
            return
        expiration_input.input.validate(expiration_input.value_raw)

    def on_input_changed(self) -> None:
        self._update_expiration_info_label()

    def create_dialog_content(self) -> ComposeResult:
        if self._is_signed:
            yield Static(
                "Warning: modifying expiration will invalidate existing signatures.",
                id="signed-warning",
            )
        yield DynamicLabel(
            obj_to_watch=self.world,
            attribute_name="node_reactive",
            callback=self._get_head_block_time_text,
            first_try_callback=lambda: self.node.cached.is_online_status_known,
            id_="head-block-time",
        )
        yield Static(
            "You can enter:\n  \u2022 relative time: 30m, 1h, 12h 30m\n  \u2022 absolute time: 2025-01-01T00:00:00",
            id="enter-description",
        )
        yield ExpirationInput(
            "Expiration time",
            value=self._expiration_value,
            always_show_title=True,
            validators=[
                ExpirationValidator(
                    head_block_time_provider=self._get_head_block_time,
                    metadata_block_time=None if self._is_signed else self._metadata_block_time,
                )
            ],
            id="expiration-delta-input",
        )
        yield DynamicLabel(
            obj_to_watch=self.world,
            attribute_name="node_reactive",
            callback=self._get_expiration_info_text,
            first_try_callback=lambda: self.node.cached.is_online_status_known,
            id_="expiration-info",
        )

    async def _perform_confirmation(self) -> bool:
        return self.query_exactly_one(ExpirationInput).validate_passed()

    def _close_when_confirmed(self) -> None:
        result = self.query_exactly_one(ExpirationInput).value_or_none(notify_on_value_error=False)
        self.dismiss(result=result)

    def _close_when_cancelled(self) -> None:
        self.dismiss(result=None)
