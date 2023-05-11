from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar, get_type_hints

import inflection

from clive.__private.abstract_class import AbstractClass
from clive.__private.core.beekeeper.model import JSONRPCRequest, JSONRPCResponse

if TYPE_CHECKING:
    from collections.abc import Callable

    from typing_extensions import Self

    from clive.__private.core.node import Node

P = ParamSpec("P")
R = TypeVar("R")


class Api(AbstractClass):
    def __init__(self, node: Node):
        self._node = node

    @staticmethod
    def method(func: Callable[P, R]) -> Callable[P, R | JSONRPCResponse[Any]]:
        @wraps(func)
        def wrapper(this: Self, /, **kwargs: P.kwargs) -> R | JSONRPCResponse[Any]:
            return_type: type[R] = get_type_hints(func)["return"]
            endpoint = this.__get_endpoint(func)
            request = JSONRPCRequest(method=endpoint, params=kwargs)
            return this._node.send(request, expect_type=return_type)

        return wrapper  # type: ignore

    def __get_endpoint(self, func: Callable[..., Any]) -> str:
        return f"{inflection.underscore(self.__class__.__name__)}.{func.__name__}"
