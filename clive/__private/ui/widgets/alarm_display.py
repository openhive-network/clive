from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.dynamic_widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.profile_data import ProfileData


class AutoUseWorkingAccount:
    """Used to indicate that the working account should be used in the alarm display."""


class AlarmDisplay(DynamicLabel):
    DEFAULT_CSS = """
    AlarmDisplay {
        text-style: bold;
        background: $error-lighten-3;
        padding: 0 1;
        color: $text;

        &.-no-alarm {
            background: $success-lighten-3;
        }
    }
    """

    def __init__(
        self,
        account: TrackedAccount | AutoUseWorkingAccount = AutoUseWorkingAccount(),  # noqa: B008
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        self._account = account
        super().__init__(
            self.world,
            "profile_data",
            self._update_callback,
            first_try_callback=self._first_try_alarms_callback,
            id_=id_,
            classes=classes,
        )

    @property
    def account(self) -> TrackedAccount:
        account = self.profile_data.accounts.working if self._is_in_auto_working_account_mode() else self._account
        assert not isinstance(account, AutoUseWorkingAccount), "Account should be ensured to be a TrackedAccount."
        return account

    def _update_callback(self, pd: ProfileData) -> str:
        class_name = "-no-alarm"
        no_alarms_info = "No alarms"

        if self._is_in_auto_working_account_mode() and not pd.accounts.has_working_account:
            self.add_class(class_name)
            return no_alarms_info

        alarm_count = len(self.account.alarms.harmful_alarms)

        if alarm_count:
            self.remove_class(class_name)
            return f"{alarm_count} ALARM{'S' if alarm_count > 1 else ''}"

        self.add_class(class_name)
        return no_alarms_info

    def _first_try_alarms_callback(self, pd: ProfileData) -> bool:
        if not self._is_in_auto_working_account_mode():
            return self.account.is_alarms_data_available

        if pd.accounts.has_working_account:
            return pd.accounts.working.is_alarms_data_available

        # if the working account is not set, we cannot display alarms, so True is returned to allow
        # the first attempt in _update_callback
        return True

    def _is_in_auto_working_account_mode(self) -> bool:
        return isinstance(self._account, AutoUseWorkingAccount)
