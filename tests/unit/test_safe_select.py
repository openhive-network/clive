from __future__ import annotations

from typing import Final

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Select

from clive.__private.ui.widgets.select.safe_select import EmptySelect, SafeSelect, SingleSelect
from clive.exceptions import NoItemSelectedError


def test_min_amount_of_items() -> None:
    # ARRANGE
    expected: Final[int] = 2

    # ASSERT
    assert expected == SafeSelect.MIN_AMOUNT_OF_ITEMS


@pytest.mark.parametrize("amount", list(range(SafeSelect.MIN_AMOUNT_OF_ITEMS + 1)))
def test_creating_safe_select_is_possible_with_arbitrary_num_of_options(amount: int) -> None:
    # ACT & ASSERT
    SafeSelect([(str(i), i) for i in range(amount)])


def test_getting_safe_select_value_with_no_items() -> None:
    # ARRANGE
    select = SafeSelect([])  # type: ignore[var-annotated]

    # ACT & ASSERT
    assert isinstance(select._content, EmptySelect)
    with pytest.raises(NoItemSelectedError, match="No item is selected yet from"):
        select.value  # noqa: B018


def test_getting_safe_select_value_with_one_item() -> None:
    # ARRANGE
    expected_value: Final[int] = 1
    select = SafeSelect[int]([(str(expected_value), expected_value)])

    # ACT & ASSERT
    assert isinstance(select._content, SingleSelect)
    assert select.value == expected_value


class SelectApp(App[None]):
    def compose(self) -> ComposeResult:
        yield SafeSelect([(str(i), i) for i in range(10)])


async def test_getting_safe_select_value_with_min_amount_of_items_and_nothing_selected() -> None:
    async with SelectApp().run_test() as pilot:
        app: SelectApp = pilot.app  # type: ignore[assignment]
        select = app.query_exactly_one(SafeSelect)

        assert isinstance(select._content, Select)
        with pytest.raises(NoItemSelectedError, match="No item is selected yet from"):
            select.value  # noqa: B018


class SelectAppInitial(App[None]):
    INITIAL_VALUE: Final[int] = 3

    def compose(self) -> ComposeResult:
        yield SafeSelect([(str(i), i) for i in range(10)], value=self.INITIAL_VALUE)


async def test_getting_safe_select_value_with_min_amount_of_items_and_default_selected() -> None:
    async with SelectAppInitial().run_test() as pilot:
        app: SelectAppInitial = pilot.app  # type: ignore[assignment]
        select = app.query_exactly_one(SafeSelect)

        assert isinstance(select._content, Select)
        assert select.value == app.INITIAL_VALUE
