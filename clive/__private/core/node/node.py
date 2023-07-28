from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, overload

from clive.__private.core._async import asyncio_run
from clive.__private.core.beekeeper.model import JSONRPCResponse
from clive.__private.core.communication import Communication
from clive.__private.core.node.api.apis import Apis
from clive.exceptions import CommunicationError

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.model import JSONRPCRequest
    from clive.__private.core.profile_data import ProfileData
    from clive.core.url import Url

T = TypeVar("T")


class Node:
    def __init__(self, profile_data: ProfileData) -> None:
        self.__profile_data = profile_data
        self.api = Apis(self)
        self.__network_type = ""
        self.__sync_node_version()

    @property
    def network_type(self) -> str:
        return self.__network_type

    @property
    def address(self) -> Url:
        return self.__profile_data._node_address

    @address.setter
    def address(self, address: Url) -> None:
        self.__profile_data._node_address = address
        self.__sync_node_version()

    @overload
    async def send(self, request: JSONRPCRequest, *, expect_type: None = None) -> JSONRPCResponse[Any]:
        ...

    @overload
    async def send(self, request: JSONRPCRequest, *, expect_type: type[T]) -> T:
        ...

    async def send(self, request: JSONRPCRequest, *, expect_type: type[T] | None = None) -> T | JSONRPCResponse[Any]:
        response = await Communication.arequest(str(self.address), data=request.json(by_alias=True))
        data = response.json()

        if not expect_type:
            return JSONRPCResponse(**data)

        return expect_type(**data)

    @property
    def chain_id(self) -> str:
        return asyncio_run(self.api.database_api.get_config()).HIVE_CHAIN_ID

    def __sync_node_version(self) -> None:
        if self.address:
            try:
                self.__network_type = asyncio_run(self.api.database_api.get_version()).node_type
            except CommunicationError:
                self.__network_type = "no connection"
