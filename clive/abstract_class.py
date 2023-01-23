from abc import ABC
from typing import Any


class AbstractClass(ABC):
    """
    Abstract class that marks if some class cannot be instantiated.
    Even when no abstract methods were defined, this class cannot be instantiated. (default ABC allows for that)
    """

    def __new__(cls, *args, **kwargs) -> Any:  # type: ignore
        if AbstractClass in cls.__bases__:
            raise TypeError(f"Abstract class `{cls.__name__}` cannot be instantiated.")

        return super().__new__(cls, *args, **kwargs)
