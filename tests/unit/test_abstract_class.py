from abc import abstractmethod
from typing import Generic, TypeVar

import pytest

from clive.abstract_class import AbstractClass

T = TypeVar("T")


class MockPlainAbstract(AbstractClass):
    pass


class MockAbstractWithGenerics(Generic[T], AbstractClass):
    pass


class MockAbstractWithAbstractMethod(AbstractClass):
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


@pytest.mark.parametrize("cls", [MockPlainAbstract, MockAbstractWithGenerics])
def test_instantiating_class_inheriting_from_abstract_class(cls: type) -> None:
    with pytest.raises(TypeError) as exception:
        cls()

    assert str(exception.value) == f"Abstract class `{cls.__name__}` cannot be instantiated."


def test_instantiating_class_inheriting_from_abstract_class_with_abstract_method() -> None:
    with pytest.raises(TypeError) as exception:
        MockSubclassWithoutAbstractMethod()  # type: ignore

    assert (
        str(exception.value)
        == "Can't instantiate abstract class MockSubclassWithoutAbstractMethod with abstract methods abstract_method"
    )


@pytest.mark.parametrize("cls", [MockValidPlainSubclass, MockValidSubclassWithAbstractMethod])
def test_instantiating_valid_subclass(cls: type) -> None:
    cls()
