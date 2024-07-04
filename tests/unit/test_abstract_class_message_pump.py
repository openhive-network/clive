from __future__ import annotations

from abc import abstractmethod

import pytest

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


class MockValidSubclassWithAbstractMethod(MockAbstractWithAbstractMethod):
    def abstract_method(self) -> None:
        pass


def test_instantiating_class_inheriting_from_abstract_class_with_abstract_method() -> None:
    # ARRANGE
    expected_error_message = (
        "Can't instantiate abstract class MockSubclassWithoutAbstractMethod with abstract method abstract_method"
    )

    # ACT & ASSERT
    with pytest.raises(TypeError) as exception:
        MockSubclassWithoutAbstractMethod()  # type: ignore[abstract]

    assert str(exception.value) == expected_error_message


@pytest.mark.parametrize("cls", [MockValidPlainSubclass, MockValidSubclassWithAbstractMethod])
def test_instantiating_valid_subclass(cls: type) -> None:
    cls()
