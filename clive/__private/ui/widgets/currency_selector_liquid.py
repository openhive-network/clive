from __future__ import annotations

from clive.__private.ui.widgets.currency_selector import CurrencySelector


class CurrencySelectorLiquid(CurrencySelector):
    """Currency selector using in operations, there are always two options two choose - HIVE or HBD"""

    def __init__(self) -> None:
        super().__init__("HIVE", "HBD")
