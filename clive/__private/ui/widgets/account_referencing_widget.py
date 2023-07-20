from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel

if TYPE_CHECKING:
    from collections.abc import Callable

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

    def create_dynamic_label(self, foo: Callable[[], str], classes: str | None = None) -> DynamicLabel:
        return DynamicLabel(
            self.app.world,
            "profile_data",
            lambda _: foo() if self._account.name else "NULL",
            classes=classes,
        )
