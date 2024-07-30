from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.widgets.buttons.one_line_button import OneLineButton
from clive.__private.ui.widgets.dynamic_widgets.dynamic_one_line_button import DynamicOneLineButton

if TYPE_CHECKING:
    from clive.__private.core.profile_data import ProfileData
    from clive.__private.storage.accounts import TrackedAccount


class AlarmDisplay(DynamicOneLineButton):
    DEFAULT_CSS = """
    AlarmDisplay {
        OneLineButton {
            width: 1fr;
        }
    }
    """

    def __init__(
        self,
        account: TrackedAccount | None = None,
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        def update_callback(pd: ProfileData) -> str:
            if account is None and not pd.is_working_account_set():
                self.tooltip = None
                return "No account"

            checked_account = account if account is not None else pd.working_account
            alarm_count = len(checked_account.alarms.harmful_alarms)

            if alarm_count:
                self._widget.variant = "error"
                self.tooltip = "See alarms"
                return f"{alarm_count} ALARM{'S' if alarm_count > 1 else ''}"

            self.tooltip = None
            self._widget.variant = "success"
            return "No alarms"

        super().__init__(
            self.world,
            "profile_data",
            update_callback,
            first_try_callback=lambda profile_data: all(
                acc.is_alarms_data_available for acc in profile_data.get_tracked_accounts()
            ),
            id_=id_,
            classes=classes,
            variant="error",
        )
        self._account = account

    @on(OneLineButton.Pressed)
    def push_alarms_details(self) -> None:
        from clive.__private.ui.account_details.account_details import AccountDetails

        if isinstance(self.app.screen, AccountDetails):
            return

        if self._account is None and not self.world.profile_data.is_working_account_set():
            return

        account = self._account if self._account is not None else self.world.profile_data.working_account
        self.app.push_screen(AccountDetails(account))
