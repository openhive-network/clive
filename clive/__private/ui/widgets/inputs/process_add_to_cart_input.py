from __future__ import annotations

from clive.__private.ui.widgets.inputs.clive_input import CliveInput


class ProcessAddToCartInput(CliveInput):
    """
    Input which will trigger add_to_cart after emitted `Submitted` event.

    Notice: that's working when is used with a `OperationActionBindings`.
    """

    class Submitted(CliveInput.Submitted):
        """Event emitted when the `ProcessAddToCartInput` is submitted."""
