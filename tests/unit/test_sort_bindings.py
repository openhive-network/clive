from __future__ import annotations

from typing import Any, Callable, Final

from clive.ui.app import Clive

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


def dicts_equal_with_order(dict_a: dict[Any, Any], dict_b: dict[Any, Any]) -> bool:
    """
    Python dictionaries are insertion ordered as of Python 3.6
    While comparing with simple ==, it won't check the order, just their contents.
    """
    return list(dict_a.keys()) == list(dict_b.keys()) and dict_a == dict_b


def test_sort_fn_bindings() -> None:
    # ACT & ASSERT
    assert dicts_equal_with_order(METHOD_TO_TEST(FN_BINDINGS_UNSORTED), FN_BINDINGS_SORTED)


def test_sort_fn_and_char_bindings() -> None:
    # ARRANGE
    additional_character_bindings = {"a": "a", "b": "b", "c": "c"}
    dict_to_sort = FN_BINDINGS_UNSORTED | additional_character_bindings

    dict_sorted = additional_character_bindings | FN_BINDINGS_SORTED

    # ACT & ASSERT
    assert dicts_equal_with_order(METHOD_TO_TEST(dict_to_sort), dict_sorted)
