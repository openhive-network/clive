from __future__ import annotations

from abc import ABC, abstractmethod

import pytest
from textual.screen import Screen
from textual.widget import Widget

from clive.__private.abstract_class import AbstractClassMessagePump


class MockPlainAbstract(AbstractClassMessagePump):
    pass


class MockAbstractWithAbstractMethod(AbstractClassMessagePump):
    @abstractmethod
    def abstract_method(self) -> None:
        pass


class MockSubclassWithoutAbstractMethod(MockAbstractWithAbstractMethod):
    pass


class MockValidPlainSubclass(MockPlainAbstract):
    pass


class AbstractWidget(Widget, AbstractClassMessagePump):
    pass


class AbstractScreen(Screen[None], AbstractClassMessagePump):
    pass


class MockValidSubclassWithAbstractMethod(MockAbstractWithAbstractMethod):
    def abstract_method(self) -> None:
        pass


def test_textual_still_errors_with_abc_inheritance() -> None:
    # ARRANGE
    expected_error_message = (
        "metaclass conflict: the metaclass of a derived class must be a"
        " (non-strict) subclass of the metaclasses of all its bases"
    )

    # ACT & ASSERT
    with pytest.raises(TypeError) as exception:

        class InvalidAbstractScreen(Screen[None], ABC):  # type: ignore[metaclass]
            pass

    assert str(exception.value) == expected_error_message


def test_instantiating_class_inheriting_from_abstract_class_with_abstract_method() -> None:
    # ARRANGE
    expected_error_message = (
        "Can't instantiate abstract class MockSubclassWithoutAbstractMethod without an implementation for"
        " abstract method 'abstract_method'"
    )

    # ACT & ASSERT
    with pytest.raises(TypeError) as exception:
        MockSubclassWithoutAbstractMethod()  # type: ignore[abstract]

    assert str(exception.value) == expected_error_message


@pytest.mark.parametrize(
    "cls", [MockValidPlainSubclass, MockValidSubclassWithAbstractMethod, AbstractWidget, AbstractScreen]
)
def test_instantiating_valid_subclass(cls: type) -> None:
    cls()
