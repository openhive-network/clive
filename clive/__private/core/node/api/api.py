from __future__ import annotations

from abc import ABC
from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar, get_type_hints

from clive.__private.core.formatters.case import underscore
from clive.__private.models.aliased import JSONRPCRequest

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from typing_extensions import Self

    from clive.__private.core.node.node import BaseNode


P = ParamSpec("P")
R = TypeVar("R")


class Api(ABC):  # noqa: B024
    def __init__(self, node: BaseNode) -> None:
        self._node = node

    @staticmethod
    def method(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(this: Self, /, **kwargs: P.kwargs) -> R:
            return_type: type[R] = get_type_hints(func)["return"]
            endpoint = this.__get_endpoint(func)
            for key in list(kwargs.keys()):
                if key.endswith("_"):
                    kwargs[key.rstrip("_")] = kwargs.pop(key)
            request = JSONRPCRequest(method=endpoint, params=kwargs)
            return await this._node.handle_request(request, expect_type=return_type)  # type: ignore[type-var]

        return wrapper  # type: ignore[return-value]

    def __get_endpoint(self, func: Callable[..., Any]) -> str:
        return f"{underscore(self.__class__.__name__)}.{func.__name__}"
