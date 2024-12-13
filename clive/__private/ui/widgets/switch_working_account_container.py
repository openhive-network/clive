from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual import on
from textual.containers import Container
from textual.reactive import var

from clive.__private.core.accounts.accounts import TrackedAccount, WorkingAccount
from clive.__private.core.accounts.exceptions import AccountAlreadyExistsError
from clive.__private.core.clive_import import get_clive
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.widgets.clive_basic import CliveRadioButton, CliveRadioSet
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from clive.__private.ui.widgets.section import Section, SectionBody

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from typing_extensions import TypeIs

    from clive.__private.core.profile import Profile


class AccountRadioButton(CliveRadioButton):
    WORKING_ACCOUNT_IDENTIFIER: Final[str] = "[yellow italic](working)[/]"

    def __init__(self, account: TrackedAccount) -> None:
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

    def __init__(self, *, value: bool) -> None:
        super().__init__(label="(no working account)", value=value)


class NoTrackedAccounts(NoContentAvailable):
    NO_TRACKED_ACCOUNTS_MESSAGE: Final[str] = "You have no tracked accounts"

    def __init__(self) -> None:
        super().__init__(self.NO_TRACKED_ACCOUNTS_MESSAGE)


class NoWorkingAccountSelected:
    """Class using to indicate that no working account is selected."""


def get_default_profile() -> Profile:
    app = get_clive().app_instance()
    return app.world.profile.copy()


class SwitchWorkingAccountContainer(Container, CliveWidget):
    """Container that displays all tracked accounts (working + watched) and allows to switch between them."""

    DEFAULT_CSS = get_css_from_relative_path(__file__)

    local_profile: Profile = var(get_default_profile, init=False)  # type: ignore[assignment, arg-type]
    """Reactive to provide a single state of profile across the widget."""

    def __init__(self, *, show_title: bool = True) -> None:
        super().__init__()
        self._show_title = show_title

        self._selected_account: TrackedAccount | NoWorkingAccountSelected = (
            self._get_current_state_for_selected_account(self.local_profile)
        )

    def on_mount(self) -> None:
        def delegate_work_rebuild_tracked_accounts(profile: Profile) -> None:
            self.run_worker(self._rebuild_tracked_accounts(profile))

        self.watch(self.world, "profile", self._update_local_profile)
        self.watch(self, "local_profile", delegate_work_rebuild_tracked_accounts)

    def _update_local_profile(self, profile: Profile) -> None:
        if self.local_profile.accounts.tracked == profile.accounts.tracked:
            # nothing to update when tracked accounts have not changed
            return

        self.local_profile = profile.copy()

    async def _rebuild_tracked_accounts(self, profile: Profile) -> None:
        self._handle_selected_account_changed(profile)

        with self.app.batch_update():
            section_body = self.query_exactly_one(SectionBody)

            await section_body.query("*").remove()
            await section_body.mount(self._create_tracked_accounts_content(profile))

    def compose(self) -> ComposeResult:
        with Section("Switch working account" if self._show_title else None):
            yield self._create_tracked_accounts_content(self.local_profile)

    def _create_radio_buttons(self, profile: Profile) -> list[AccountRadioButton | NoWorkingAccountRadioButton]:
        """
        Create radio buttons for all tracked accounts and optionally a no working account button.

        If there is no working account, the additional no working account button is selected.
        """
        radio_buttons: list[AccountRadioButton | NoWorkingAccountRadioButton] = [
            AccountRadioButton(account) for account in profile.accounts.tracked
        ]
        if not profile.accounts.has_working_account:
            radio_buttons.append(NoWorkingAccountRadioButton(value=True))
        return radio_buttons

    def _create_tracked_accounts_content(self, profile: Profile) -> CliveRadioSet | NoTrackedAccounts:
        if not profile.accounts.has_tracked_accounts:
            return NoTrackedAccounts()

        return CliveRadioSet(*self._create_radio_buttons(profile))

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

        try:
            self.profile.accounts.switch_working_account(new_working_account)
        except AccountAlreadyExistsError:
            return

        self._perform_actions_after_accounts_modification()

    def _perform_actions_after_accounts_modification(self) -> None:
        self.app.trigger_profile_watchers()
        self.app.update_alarms_data_asap()

    def _handle_selected_account_changed(self, profile: Profile) -> None:
        """Due to the dynamic nature, we must take into account that tracked accounts may be modified elsewhere."""
        self._selected_account = self._get_current_state_for_selected_account(profile)

    def _get_current_state_for_selected_account(self, profile: Profile) -> WorkingAccount | NoWorkingAccountSelected:
        return profile.accounts.working if profile.accounts.has_working_account else NoWorkingAccountSelected()

    @property
    def _is_current_working_account_selected(self) -> bool:
        if self._is_no_working_account_selected(self._selected_account):
            return False

        return self.profile.accounts.is_account_working(self._selected_account)

    def _is_no_working_account_selected(self, value: object) -> TypeIs[NoWorkingAccountSelected]:
        return isinstance(value, NoWorkingAccountSelected)
