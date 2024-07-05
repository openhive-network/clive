from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Container
from textual.reactive import var

from clive.__private.core.clive_import import get_clive
from clive.__private.storage.accounts import Account, WorkingAccount
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_radio_button import CliveRadioButton
from clive.__private.ui.widgets.clive_radio_set import CliveRadioSet
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.section import Section, SectionBody

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from typing_extensions import TypeIs

    from clive.__private.core.profile_data import ProfileData


class AccountRadioButton(CliveRadioButton):
    WORKING_ACCOUNT_IDENTIFIER: Final[str] = "[yellow italic](working)[/]"

    def __init__(self, account: Account) -> None:
        is_working = isinstance(account, WorkingAccount)
        self.account = account
        super().__init__(
            label=self._create_button_label(is_working=is_working),
            value=is_working,
        )

    def remove_working_account_label(self) -> None:
        self.label = self.account.name  # type: ignore[assignment]

    def set_working_account_label(self) -> None:
        self.label = self._create_button_label(is_working=True)  # type: ignore[assignment]

    def _create_button_label(self, *, is_working: bool) -> str:
        return f"{self.account.name} {self.WORKING_ACCOUNT_IDENTIFIER if is_working else ''}"


class NoWorkingAccountRadioButton(CliveRadioButton):
    """
    Indicates no working account option.

    Button is created because the textual `RadioSet` does not support deselecting radio buttons
    and situations where there are no radio buttons selected. This approach is not ideal, but this way we do not
    have to change the `RadioSet` code.
    """

    def __init__(self, *, is_working_account_set: bool) -> None:
        super().__init__(label="(no working account)", value=is_working_account_set)


class NoTrackedAccounts(NoContentAvailable):
    NO_TRACKED_ACCOUNTS_MESSAGE: Final[str] = "You have no tracked accounts"

    def __init__(self) -> None:
        super().__init__(self.NO_TRACKED_ACCOUNTS_MESSAGE)


class NoWorkingAccountSelected:
    """Class using to indicate that no working account is selected."""


def get_default_profile_data() -> ProfileData:
    app = get_clive().app_instance()
    return app.world.profile_data.copy()


class SwitchWorkingAccountContainer(Container, CliveWidget):
    """Container that displays all tracked accounts (working + watched) and allows to switch between them."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    local_profile_data: ProfileData = var(get_default_profile_data, init=False)  # type: ignore[assignment, arg-type]
    """Reactive to provide a single state of profile data across the widget."""

    def __init__(self, *, show_title: bool = True) -> None:
        super().__init__()
        self._show_title = show_title

        self._selected_account: Account | NoWorkingAccountSelected = self._get_current_state_for_selected_account(
            self.local_profile_data
        )

    def on_mount(self) -> None:
        def delegate_work_rebuild_tracked_accounts(profile_data: ProfileData) -> None:
            self.run_worker(self._rebuild_tracked_accounts(profile_data))

        self.watch(self.world, "profile_data", self._update_local_profile_data)
        self.watch(self, "local_profile_data", delegate_work_rebuild_tracked_accounts)

    def _update_local_profile_data(self, profile_data: ProfileData) -> None:
        if self.local_profile_data.tracked_accounts_sorted == profile_data.tracked_accounts_sorted:
            # nothing to update when tracked accounts have not changed
            return

        self.local_profile_data = profile_data.copy()

    async def _rebuild_tracked_accounts(self, profile_data: ProfileData) -> None:
        self._handle_selected_account_changed(profile_data)

        with self.app.batch_update():
            section_body = self.query_one(SectionBody)

            await section_body.query("*").remove()
            await section_body.mount(self._create_tracked_accounts_content(profile_data))

    def compose(self) -> ComposeResult:
        with Section("Switch working account" if self._show_title else None):
            yield self._create_tracked_accounts_content(self.local_profile_data)

    def _create_radio_buttons(self, profile_data: ProfileData) -> list[AccountRadioButton | CliveRadioButton]:
        """Create radio buttons for all tracked accounts and a no working account button."""
        tracked_account_radios = [AccountRadioButton(account) for account in profile_data.tracked_accounts_sorted]
        no_working_account_radio = NoWorkingAccountRadioButton(
            is_working_account_set=not profile_data.is_working_account_set()
        )

        return [*tracked_account_radios, no_working_account_radio]

    def _create_tracked_accounts_content(self, profile_data: ProfileData) -> CliveRadioSet | NoTrackedAccounts:
        if not profile_data.has_tracked_accounts():
            return NoTrackedAccounts()

        return CliveRadioSet(*self._create_radio_buttons(profile_data))

    @on(CliveRadioSet.Changed)
    def change_selected_working_account(self, event: CliveRadioSet.Changed) -> None:
        for account_button in self.query(AccountRadioButton):
            account_button.remove_working_account_label()

        radio_button = event.pressed

        if isinstance(radio_button, NoWorkingAccountRadioButton):
            # There is only one case where the `AccountRadioButton` is not used - when a working account is removed
            self._selected_account = NoWorkingAccountSelected()
            return

        assert isinstance(radio_button, AccountRadioButton), f"Expected AccountRadioButton, got {type(radio_button)}"

        radio_button.set_working_account_label()
        self._selected_account = radio_button.account

    def confirm_selected_working_account(self) -> None:
        new_working_account = (
            None if self._is_no_working_account_selected(self._selected_account) else self._selected_account
        )

        self.profile_data.switch_working_account(new_working_account)
        self._perform_actions_after_accounts_modification()

    def _perform_actions_after_accounts_modification(self) -> None:
        self.app.trigger_profile_data_watchers()
        self.app.update_alarms_data_asap()

    def _handle_selected_account_changed(self, profile_data: ProfileData) -> None:
        """Due to the dynamic nature, we must take into account that tracked accounts may be modified elsewhere."""
        self._selected_account = self._get_current_state_for_selected_account(profile_data)

    def _get_current_state_for_selected_account(
        self, profile_data: ProfileData
    ) -> WorkingAccount | NoWorkingAccountSelected:
        return profile_data.working_account if profile_data.is_working_account_set() else NoWorkingAccountSelected()

    @property
    def _is_current_working_account_selected(self) -> bool:
        if self._is_no_working_account_selected(self._selected_account):
            return False

        return self.profile_data.is_account_working(self._selected_account)

    def _is_no_working_account_selected(self, value: object) -> TypeIs[NoWorkingAccountSelected]:
        return isinstance(value, NoWorkingAccountSelected)
