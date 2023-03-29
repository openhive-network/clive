from __future__ import annotations

from functools import lru_cache
from inspect import isawaitable, signature
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


@lru_cache(maxsize=2048)
def __count_parameters(callback: Callable[..., Any]) -> int:
    """Count the number of parameters in a callable"""
    return len(signature(callback).parameters)


async def invoke(callback: Callable[..., Any], *params: Any) -> Any:
    """
    Invoke a callback with an arbitrary number of parameters.

    Args:
    callback: The callable to be invoked.

    Returns:
        The return value of the invoked callable.
    """
    parameter_count = __count_parameters(callback)
    result = callback(*params[:parameter_count])
    if isawaitable(result):
        result = await result
    return result
