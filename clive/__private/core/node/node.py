from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, overload

from clive.__private.core.beekeeper.model import JSONRPCResponse
from clive.__private.core.communication import Communication
from clive.__private.core.node.api.apis import Apis

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.model import JSONRPCRequest
    from clive.__private.core.profile_data import ProfileData
    from clive.core.url import Url

T = TypeVar("T")


class Node:
    def __init__(self, profile_data: ProfileData) -> None:
        self.__profile_data = profile_data
        self.api = Apis(self)

    @property
    def address(self) -> Url:
        return self.__profile_data.node_address

    @address.setter
    def address(self, address: Url) -> None:
        self.__profile_data.node_address = address

    @overload
    def send(self, request: JSONRPCRequest, *, expect_type: None = None) -> JSONRPCResponse[Any]:
        ...

    @overload
    def send(self, request: JSONRPCRequest, *, expect_type: type[T]) -> T:
        ...

    def send(self, request: JSONRPCRequest, *, expect_type: type[T] | None = None) -> T | JSONRPCResponse[Any]:
        response = Communication.request(str(self.address), data=request.dict(by_alias=True))
        data = response.json()

        if not expect_type:
            return JSONRPCResponse(**data)

        return expect_type(**data)
