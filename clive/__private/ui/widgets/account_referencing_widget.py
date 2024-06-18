from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from collections.abc import Callable

    from clive.__private.core.profile_data import ProfileData
    from clive.__private.storage.accounts import Account


class AccountReferencingWidget(CliveWidget):
    def __init__(
        self,
        account: Account,
        name: str | None = None,
        classes: str | None = None,
    ) -> None:
        self._account = account
        super().__init__(name=name, classes=classes)

    def create_dynamic_label(
        self,
        foo: Callable[[], str],
        *,
        classes: str | None = None,
        init: bool = True,
    ) -> DynamicLabel:
        return DynamicLabel(
            self.app.world,
            "profile_data",
            lambda: foo() if self._account.name else "NULL",
            first_try_callback=self._check_if_account_node_data_is_available,
            classes=classes,
            init=init,
        )

    def _check_if_account_node_data_is_available(self, profile_data: ProfileData) -> bool:
        if profile_data.is_working_account_set() and self._account == profile_data.working_account:
            return profile_data.working_account.is_node_data_available
        for account in profile_data.watched_accounts:
            if account == self._account:
                return account.is_node_data_available
        return False
