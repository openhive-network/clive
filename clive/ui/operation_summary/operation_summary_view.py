from __future__ import annotations

from typing import TYPE_CHECKING

from clive.ui.components.side_panel import SidePanel
from clive.ui.operation_summary.operation_summary_buttons import OperationSummaryButtons
from clive.ui.operation_summary.operation_summary_panel import OperationSummaryPanel
from clive.ui.views.side_pane_based import SidePanelBased

if TYPE_CHECKING:
    from clive.models.operation import Operation

Main = OperationSummaryPanel
Side = SidePanel["OperationSummaryView"]
Buttons = OperationSummaryButtons


class OperationSummaryView(SidePanelBased[Main, Side, Buttons]):
    def __init__(self, operation: Operation):
        super().__init__(OperationSummaryPanel(self, operation), SidePanel(self), OperationSummaryButtons(self))
