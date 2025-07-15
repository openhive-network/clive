from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.widgets.buttons import OneLineButton
from clive.__private.ui.widgets.dynamic_widgets.dynamic_one_line_button import DynamicOneLineButtonUnfocusable

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.profile import Profile


class AutoUseWorkingAccount:
    """Used to indicate that the working account should be used in the alarm display."""


class AlarmDisplay(DynamicOneLineButtonUnfocusable):
    def __init__(
        self,
        account: TrackedAccount | AutoUseWorkingAccount = AutoUseWorkingAccount(),  # noqa: B008
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        self._account = account
        super().__init__(
            self.world,
            "profile_reactive",
            self._update_callback,
            first_try_callback=self._first_try_alarms_callback,
            id_=id_,
            classes=classes,
        )
        self._widget.id = "alarm-display-button"

    @property
    def account(self) -> TrackedAccount:
        account = self.profile.accounts.working if self._is_in_auto_working_account_mode() else self._account
        assert not isinstance(account, AutoUseWorkingAccount), "Account should be ensured to be a TrackedAccount."
        return account

    def _update_callback(self, profile: Profile) -> str:
        no_alarms_info = "No alarms"

        if self._is_in_auto_working_account_mode() and not profile.accounts.has_working_account:
            self._change_to_no_alarms_info()
            return no_alarms_info

        alarm_count = len(self.account.alarms.harmful_alarms)

        if alarm_count:
            self._change_to_alarm_count()
            return f"{alarm_count} ALARM{'S' if alarm_count > 1 else ''}"

        self._change_to_no_alarms_info()
        return no_alarms_info

    def _first_try_alarms_callback(self, profile: Profile) -> bool:
        if not self._is_in_auto_working_account_mode():
            return self.account.is_alarms_data_available

        if profile.accounts.has_working_account:
            return profile.accounts.working.is_alarms_data_available

        # if the working account is not set, we cannot display alarms, so True is returned to allow
        # the first attempt in _update_callback
        return True

    def _change_to_no_alarms_info(self) -> None:
        self._widget.variant = "success"
        self.tooltip = None

    def _change_to_alarm_count(self) -> None:
        self._widget.variant = "error"
        self.tooltip = "See account alarms"

    def _is_in_auto_working_account_mode(self) -> bool:
        return isinstance(self._account, AutoUseWorkingAccount)

    @CliveScreen.prevent_action_when_no_accounts_node_data()
    @on(OneLineButton.Pressed, "#alarm-display-button")
    def push_account_details_screen(self) -> None:
        from clive.__private.ui.screens.account_details.account_details import AccountDetails

        def is_current_screen_account_details() -> bool:
            return isinstance(self.app.screen, AccountDetails)

        if is_current_screen_account_details():
            return

        if self._is_in_auto_working_account_mode() and not self.profile.accounts.has_working_account:
            return

        async def impl() -> None:
            if self.app.current_mode == "settings":
                await self.app.switch_mode_with_reset("dashboard")
            self.app.push_screen(AccountDetails(self.account))

        self.app.run_worker_with_screen_remove_guard(impl())
