from __future__ import annotations

from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from test_tools import logger

from clive.__private.core.node.api.apis import Apis
from clive.exceptions import CliveError, CommunicationError
from schemas.__private.hive_factory import HiveError, HiveResult, T

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType

    from typing_extensions import Self

    from clive.__private.core.beekeeper.model import JSONRPCRequest
    from clive.__private.core.communication import Communication
    from clive.__private.core.profile_data import ProfileData
    from clive.core.url import Url


class ResponseNotReadyError(CliveError):
    pass


class BaseNode:
    @abstractmethod
    async def handle_request(self, request: JSONRPCRequest, *, expect_type: type[T]) -> T:
        ...


class _DelayedResponseWrapper:
    def __init__(self, url: str, request: str, expected_type: type[T]) -> None:
        with self.__omit_overriden_set_get_attr():
            self.__url = url
            self.__request = request
            self.__expected_type = expected_type
            self.__data: HiveResult[Any] | HiveError | None = None

    def __check_is_response_available(self) -> None:
        if self.__get_data() is None:
            raise ResponseNotReadyError

    def __get_data(self) -> Any:
        with self.__omit_overriden_set_get_attr():
            if self.__data is None:
                return None

            if isinstance(self.__data, HiveResult):
                return self.__data.result

            raise CommunicationError(url=self.__url, request=self.__request, response=self.__data)  # type: ignore[arg-type]

    def __setattr__(self, name: str, value: Any) -> None:
        self.__check_is_response_available()
        setattr(self.__get_data(), name, value)

    def __getattr__(self, name: str) -> Any:
        self.__check_is_response_available()
        return getattr(self.__get_data(), name)

    def _set_response(self, **kwargs: Any) -> None:
        with self.__omit_overriden_set_get_attr():
            self.__data = HiveResult.factory(self.__expected_type, **kwargs)

    @contextmanager
    def __omit_overridden_set_get_attr(self) -> Iterator[None]:
        original_setattr = self.__class__.__setattr__
        original_getattr = self.__class__.__getattr__

        self.__class__.__setattr__ = super().__class__.__setattr__  # type: ignore[method-assign]
        self.__class__.__getattr__ = super().__class__.__getattribute__  # type: ignore[method-assign]
        try:
            yield None
        finally:
            self.__class__.__setattr__ = original_setattr  # type: ignore[method-assign]
            self.__class__.__getattr__ = original_getattr  # type: ignore[method-assign]


@dataclass(kw_only=True)
class _BatchRequestResponseItem:
    request: str
    delayed_result: _DelayedResponseWrapper


class _BatchNode(BaseNode):
    def __init__(self, communication: Communication, url: Url) -> None:
        self.__communication = communication
        self.__url = url
        self.__batch: list[_BatchRequestResponseItem] = []
        self.api = Apis(self)

    async def handle_request(self, request: JSONRPCRequest, *, expect_type: type[T]) -> T:
        request.id_ = len(self.__batch)
        serialized_request = request.json(by_alias=True)
        delayed_result = _DelayedResponseWrapper(
            url=self.__url.as_string(), request=serialized_request, expected_type=expect_type
        )
        logger.debug("Never reached")
        self.__batch.append(_BatchRequestResponseItem(request=serialized_request, delayed_result=delayed_result))
        return delayed_result  # type: ignore[return-value]

    async def __evaluate(self) -> None:
        query = "[" + ",".join([x.request for x in self.__batch]) + "]"
        logger.debug(f"Sending batch request to {self.__url.as_string()}, request={query}")
        responses: list[dict[str, Any]] = (
            await self.__communication.arequest(url=self.__url.as_string(), data=query)
        ).json()
        assert len(responses) == len(self.__batch), "invalid amount of responses"
        for response in responses:
            request_id = int(response["id"])
            self.__batch[request_id].delayed_result._set_response(**response)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, _: type[Exception] | None, ex: Exception | None, ___: TracebackType | None) -> None:
        await self.__evaluate()


class Node(BaseNode):
    def __init__(self, communication: Communication, profile_data: ProfileData) -> None:
        self.__communication = communication
        self.__profile_data = profile_data
        self.api = Apis(self)
        self.__network_type = ""

    def batch(self) -> _BatchNode:
        """
        In this mode all requests will be send as one request.

        Usage:

        with world.node.batch() as node:
            config = await node.api.database.get_config()
            dgpo = await node.api.database.get_dynamic_global_properties()
            # dgpo.time # this will raise Error
        dgpo.time # this is legit call
        """
        return _BatchNode(communication=self.__communication, url=self.address)

    async def setup(self) -> None:
        await self.__sync_node_version()

    @property
    def network_type(self) -> str:
        return self.__network_type

    @property
    def address(self) -> Url:
        return self.__profile_data._node_address

    async def set_address(self, address: Url) -> None:
        self.__profile_data._node_address = address
        await self.__sync_node_version()

    async def handle_request(self, request: JSONRPCRequest, *, expect_type: type[T]) -> T:
        address = str(self.address)
        serialized_request = request.json(by_alias=True)
        response = await self.__communication.arequest(address, data=serialized_request)
        data = response.json()
        response_model: HiveResult[T] | HiveError = HiveResult.factory(expect_type, **data)
        if isinstance(response_model, HiveResult):
            return response_model.result
        raise CommunicationError(address, serialized_request, data)

    @property
    async def chain_id(self) -> str:
        return (await self.api.database_api.get_config()).HIVE_CHAIN_ID

    async def __sync_node_version(self) -> None:
        if self.address:
            try:
                self.__network_type = (await self.api.database_api.get_version()).node_type
            except CommunicationError:
                self.__network_type = "no connection"
