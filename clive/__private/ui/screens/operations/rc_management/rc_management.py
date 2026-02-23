from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.data_providers.rc_data_provider import RcDataProvider
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.operation_base_screen import OperationBaseScreen
from clive.__private.ui.screens.operations.rc_management.common_rc.rc_information_table import RcDataTable
from clive.__private.ui.screens.operations.rc_management.delegate_rc.delegate_rc import DelegateRc
from clive.__private.ui.widgets.clive_basic import CliveTabbedContent
from clive.__private.ui.widgets.location_indicator import LocationIndicator

if TYPE_CHECKING:
    from textual.app import ComposeResult


class RcManagement(OperationBaseScreen):
    CSS_PATH = [
        *OperationBaseScreen.CSS_PATH,
        get_relative_css_path(__file__),
    ]

    def create_left_panel(self) -> ComposeResult:
        with RcDataProvider():
            yield LocationIndicator("rc management")
            yield RcDataTable()
            with CliveTabbedContent():
                yield DelegateRc()
