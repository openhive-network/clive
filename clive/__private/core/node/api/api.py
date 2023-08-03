from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar, get_type_hints

from clive.__private.abstract_class import AbstractClass
from clive.__private.core.beekeeper.model import JSONRPCProtocol, JSONRPCRequest
from clive.__private.core.formatters.case import underscore

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
    def method(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def wrapper(this: Self, /, **kwargs: P.kwargs) -> R:
            return_type: type[R] = get_type_hints(func)["return"]
            endpoint = this.__get_endpoint(func)
            for key in list(kwargs.keys()):
                if key.endswith("_"):
                    kwargs[key.rstrip("_")] = kwargs.pop(key)
            request = JSONRPCRequest(method=endpoint, params=kwargs)

            class Response(JSONRPCProtocol):
                result: return_type  # type: ignore[valid-type]

            Response.update_forward_refs(**locals())
            return (await this._node.send(request, expect_type=Response)).result

        return wrapper  # type: ignore

    def __get_endpoint(self, func: Callable[..., Any]) -> str:
        return f"{underscore(self.__class__.__name__)}.{func.__name__}"
