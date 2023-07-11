from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from clive.__private.ui.app import Clive

if TYPE_CHECKING:
    from collections.abc import Callable

METHOD_TO_TEST: Final[Callable[[Any], Any]] = Clive._Clive__sort_bindings  # type: ignore[attr-defined]

FN_BINDINGS_UNSORTED: dict[str, str] = {
    "f4": "f4",
    "f2": "f2",
    "f1": "f1",
    "f3": "f3",
}

FN_BINDINGS_SORTED: dict[str, str] = {
    "f1": "f1",
    "f2": "f2",
    "f3": "f3",
    "f4": "f4",
}

ADDITIONAL_CHARACTER_BINDINGS: dict[str, str] = {
    "a": "a",
    "b": "b",
    "c": "c",
}


def dicts_equal_with_order(dict_a: dict[Any, Any], dict_b: dict[Any, Any]) -> bool:
    """
    Python dictionaries are insertion ordered as of Python 3.6.

    While comparing with simple ==, it won't check the order, just their contents.
    """
    return list(dict_a.keys()) == list(dict_b.keys()) and dict_a == dict_b


def test_sort_fn_bindings() -> None:
    # ACT & ASSERT
    assert dicts_equal_with_order(METHOD_TO_TEST(FN_BINDINGS_UNSORTED), FN_BINDINGS_SORTED)


def test_sort_fn_and_char_bindings() -> None:
    # ARRANGE
    dict_to_sort = FN_BINDINGS_UNSORTED | ADDITIONAL_CHARACTER_BINDINGS

    dict_sorted = ADDITIONAL_CHARACTER_BINDINGS | FN_BINDINGS_SORTED

    # ACT & ASSERT
    assert dicts_equal_with_order(METHOD_TO_TEST(dict_to_sort), dict_sorted)


def test_sorting_with_esc_binding() -> None:
    # ARRANGE
    additional_esc_binding = {"escape": "escape"}
    dict_to_sort = FN_BINDINGS_UNSORTED | ADDITIONAL_CHARACTER_BINDINGS | additional_esc_binding

    dict_sorted = additional_esc_binding | ADDITIONAL_CHARACTER_BINDINGS | FN_BINDINGS_SORTED

    # ACT & ASSERT
    assert dicts_equal_with_order(METHOD_TO_TEST(dict_to_sort), dict_sorted)
