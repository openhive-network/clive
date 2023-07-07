from __future__ import annotations

from typing import Final

import pytest

from clive.__private.ui.widgets.select.safe_select import SafeSelect
from clive.__private.ui.widgets.select.select import Select
from clive.__private.ui.widgets.select.select_item import SelectItem


def test_minimum_length() -> None:
    required: Final[int] = 2

    # ARRANGE, ACT & ASSERT
    assert required == Select.MIN_AMOUNT_OF_ITEMS


@pytest.mark.parametrize("amount", [0, 1])
def test_minimum_assert(amount: int) -> None:
    # ARRANGE, ACT & ASSERT
    with pytest.raises(ValueError, match="At least 2 items are required to use Select."):
        Select([SelectItem(None, f"{i}") for i in range(amount)], list_mount="")


@pytest.mark.parametrize("amount", list(range(Select.MIN_AMOUNT_OF_ITEMS + 1)))
def test_minimum_assert_in_safe_select(amount: int) -> None:
    # ARRANGE, ACT & ASSERT
    SafeSelect([SelectItem(None, f"{i}") for i in range(amount)], list_mount="")
