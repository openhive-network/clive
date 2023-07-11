from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal
from textual.widgets import Static

from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.dynamic_label import DynamicLabel
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.app import ComposeResult

    from clive.__private.storage.mock_database import Account


class ContainerTitle(Static):
    """A title for all containers which this screen contains"""


class AccountReferencingWidget(CliveWidget):
    """Base class for all classes that must get some information about account"""

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


class GeneralInfo(AccountReferencingWidget):
    """Contains -> account-name, reputation, last account and owner update and recovery-account"""

    def compose(self) -> ComposeResult:
        yield EllipsedStatic("ACCOUNT NAME", classes="general-info-label")
        yield EllipsedStatic("ACCOUNT REPUTATION", classes="general-info-label")
        yield EllipsedStatic("LAST OWNER UPDATE", classes="general-info-label")
        yield EllipsedStatic("LAST ACCOUNT UPDATE", classes="general-info-label")
        yield EllipsedStatic("RECOVERY ACCOUNT", classes="general-info-label")

        yield EllipsedStatic(f"@{self._account.name}", classes="general-value")
        yield self.create_dynamic_label(lambda: str(self._account.data.reputation), classes="recovery-value")
        yield self.create_dynamic_label(lambda: str(self._account.data.last_owner_update), classes="date-value")
        yield self.create_dynamic_label(lambda: str(self._account.data.last_account_update), classes="date-value")
        yield self.create_dynamic_label(lambda: self._account.data.recovery_account, classes="general-value")


class AccountRow(AccountReferencingWidget):
    def compose(self) -> ComposeResult:
        with Horizontal(), Container(id="tables"):
            yield GeneralInfo(self._account)


class UserInfo(BaseScreen):
    def create_main_panel(self) -> ComposeResult:
        yield BigTitle("User info")
        yield ContainerTitle("GENERAL INFO")
        yield AccountRow(self.app.world.profile_data.working_account)
