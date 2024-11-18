from __future__ import annotations

import asyncio
import json
from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final

from clive.__private.core.commands.data_retrieval.get_node_basic_info import GetNodeBasicInfo, NodeBasicInfoData
from clive.__private.core.communication import Communication
from clive.__private.core.node.api.apis import Apis
from clive.__private.models.schemas import JSONRPCExpectResultT, JSONRPCRequest, JSONRPCResult, get_response_model
from clive.__private.settings import safe_settings
from clive.exceptions import CliveError, CommunicationError

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType

    from typing_extensions import Self

    from clive.__private.core.profile import Profile
    from clive.__private.core.url import Url
    from clive.__private.models.schemas import Config, DynamicGlobalProperties, Version


class BatchRequestError(CliveError):
    pass


class NothingToSendError(BatchRequestError):
    pass


class ResponseNotReadyError(BatchRequestError):
    pass


class BaseNode:
    @abstractmethod
    async def handle_request(
        self, request: JSONRPCRequest, *, expect_type: type[JSONRPCExpectResultT]
    ) -> JSONRPCExpectResultT: ...


class _DelayedResponseWrapper:
    def __init__(self, url: Url, request: str, expected_type: type[JSONRPCExpectResultT]) -> None:
        super().__setattr__("_url", url)
        super().__setattr__("_request", request)
        super().__setattr__("_response", None)
        super().__setattr__("_exception", None)
        super().__setattr__("_expected_type", expected_type)

    def __check_is_response_available(self) -> None:
        if (exception := super().__getattribute__("_exception")) is not None:
            raise exception
        if self.__get_data() is None:
            raise ResponseNotReadyError

    def __get_data(self) -> Any:  # noqa: ANN401
        response = super().__getattribute__("_response")
        if response is None:
            return None

        if isinstance(response, JSONRPCResult):
            return response.result

        url = super().__getattribute__("_url")
        request = super().__getattribute__("_request")
        raise CommunicationError(
            url=url.as_string(),
            request=request,
            response=response,
        )

    def __setattr__(self, __name: str, __value: Any) -> None:  # noqa: ANN401
        self.__check_is_response_available()
        setattr(self.__get_data(), __name, __value)

    def __getattr__(self, __name: str) -> Any:  # noqa: ANN401
        self.__check_is_response_available()
        return getattr(self.__get_data(), __name)

    def _set_response(self, **kwargs: Any) -> None:
        expected_type = super().__getattribute__("_expected_type")
        endpoint = str(json.loads(self._request)["method"])
        super().__setattr__("_response", get_response_model(expected_type, endpoint, **kwargs))

    def _set_exception(self, exception: Exception) -> None:
        super().__setattr__("_exception", exception)


@dataclass(kw_only=True)
class _BatchRequestResponseItem:
    request: str
    delayed_result: _DelayedResponseWrapper


class _BatchNode(BaseNode):
    def __init__(
        self, node: Node, url: Url, communication: Communication, *, delay_error_on_data_access: bool = False
    ) -> None:
        self._node = node
        self.__url = url
        self.__communication = communication
        self.__delay_error_on_data_access = delay_error_on_data_access

        self.__batch: list[_BatchRequestResponseItem] = []
        self.api = Apis(self)

    async def handle_request(
        self, request: JSONRPCRequest, *, expect_type: type[JSONRPCExpectResultT]
    ) -> JSONRPCExpectResultT:
        request.id_ = len(self.__batch)
        serialized_request = request.json(by_alias=True)
        delayed_result = _DelayedResponseWrapper(url=self.__url, request=serialized_request, expected_type=expect_type)
        self.__batch.append(_BatchRequestResponseItem(request=serialized_request, delayed_result=delayed_result))
        return delayed_result  # type: ignore[return-value]

    async def __evaluate(self) -> None:
        query = "[" + ",".join([x.request for x in self.__batch]) + "]"

        try:
            responses: list[dict[str, Any]] = await (
                await self.__communication.arequest(url=self.__url.as_string(), data=query)
            ).json()

        except CommunicationError as error:
            if not error.is_response_available:
                self._node.cached._set_offline()

            self.__handle_evaluation_communication_error(error)
        else:
            assert len(responses) == len(self.__batch), "Invalid amount of responses"
            for response in responses:
                request_id = int(response["id"])
                self.__get_batch_delayed_result(request_id)._set_response(**response)
            self._node.cached._set_online()

    def __handle_evaluation_communication_error(self, error: CommunicationError) -> None:
        responses_from_error = error.get_response()

        if responses_from_error is None:
            self.__handle_evaluation_no_response_available(error)

            if not self.__delay_error_on_data_access:
                raise error
            return

        if isinstance(responses_from_error, list):
            assert len(responses_from_error) == len(self.__batch), "Invalid amount of responses_from_error"
            self.__handle_evaluation_error_in_multiple_responses(error, responses_from_error)
        else:
            self.__handle_evaluation_error_single_response(error, responses_from_error)

        if not self.__delay_error_on_data_access:
            raise error

    def __handle_evaluation_no_response_available(self, error: CommunicationError) -> None:
        """When there is no response available, set received error on all delayed results."""
        num_of_requests = len(self.__batch)
        for request_id in range(num_of_requests):
            self.__get_batch_delayed_result(request_id)._set_exception(error)

    def __handle_evaluation_error_in_multiple_responses(
        self, error: CommunicationError, responses: list[dict[str, Any]]
    ) -> None:
        """Certain responses might be errors, some might be good - set them on delayed results."""
        for response in responses:
            request_id = int(response["id"])
            if "error" in response:
                # creating a new instance so other responses won't be included in the error
                self.__set_communication_error_on_batch_delayed_result(error, request_id, response)
            else:
                self.__get_batch_delayed_result(request_id)._set_response(**response)

        if not self.__delay_error_on_data_access:
            raise error

    def __handle_evaluation_error_single_response(self, error: CommunicationError, response: dict[str, Any]) -> None:
        """Single response error - set it on all delayed results."""
        num_of_requests = len(self.__batch)
        for request_id in range(num_of_requests):
            self.__set_communication_error_on_batch_delayed_result(error, request_id, response)

    def __set_communication_error_on_batch_delayed_result(
        self, error: CommunicationError, request_id: int, response: dict[str, Any]
    ) -> None:
        new_error = CommunicationError(
            url=error.url,
            request=self.__batch[request_id].request,
            response=response,
        )
        self.__get_batch_delayed_result(request_id)._set_exception(new_error)

    def __get_batch_delayed_result(self, request_id: int) -> _DelayedResponseWrapper:
        return self.__batch[request_id].delayed_result

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        if not self.__is_anything_to_send():
            raise NothingToSendError

        await self.__evaluate()

    def __is_anything_to_send(self) -> bool:
        return bool(self.__batch)


class Node(BaseNode):
    DEFAULT_TIMEOUT_TOTAL_SECONDS: Final[float] = safe_settings.node.communication_timeout_total_secs

    @dataclass
    class CachedData:
        _node: Node
        _basic_info: NodeBasicInfoData | None = field(init=False, default=None)
        _online: bool | None = None
        _lock: asyncio.Lock = field(init=False, default_factory=asyncio.Lock)

        @property
        def is_basic_info_available(self) -> bool:
            """Check if basic info was fetched."""
            return self._basic_info is not None

        @property
        def is_online_status_known(self) -> bool:
            """Check if online status was fetched."""
            return self._online is not None

        @property
        def is_online_with_basic_info_available(self) -> bool:
            """Return true only when node is online and basic info is already available."""
            return self.is_online_status_known and self.online_ensure and self.is_basic_info_available

        @property
        async def basic_info(self) -> NodeBasicInfoData:
            await self._fetch_basic_info()
            assert self._basic_info is not None, "basic_info is guaranteed to be set here"
            return self._basic_info

        @property
        def basic_info_ensure(self) -> NodeBasicInfoData:
            assert self._basic_info is not None, "basic_info is not available"
            return self._basic_info

        @property
        async def config(self) -> Config:
            return (await self.basic_info).config

        @property
        def config_ensure(self) -> Config:
            return self.basic_info_ensure.config

        @property
        def config_or_none(self) -> Config | None:
            """Get the config or return None when data was not fetched yet."""
            if self.is_basic_info_available:
                return self.basic_info_ensure.config
            return None

        @property
        async def version(self) -> Version:
            return (await self.basic_info).version

        @property
        def version_ensure(self) -> Version:
            return self.basic_info_ensure.version

        @property
        def version_or_none(self) -> Version | None:
            """Get the version or return None when data was not fetched yet."""
            if self.is_basic_info_available:
                return self.basic_info_ensure.version
            return None

        @property
        async def dynamic_global_properties(self) -> DynamicGlobalProperties:
            return (await self.basic_info).dynamic_global_properties

        @property
        def dynamic_global_properties_ensure(self) -> DynamicGlobalProperties:
            return self.basic_info_ensure.dynamic_global_properties

        @property
        def dynamic_global_properties_or_none(self) -> DynamicGlobalProperties | None:
            """Get the dynamic global properties or return None when data was not fetched yet."""
            if self.is_basic_info_available:
                return self.basic_info_ensure.dynamic_global_properties
            return None

        @property
        async def online(self) -> bool:
            try:
                await self._fetch_basic_info()
            except CommunicationError as error:
                if not error.is_response_available:
                    return False
                raise

            assert self._online is not None, "online is guaranteed to be set here"
            return self._online

        @property
        def online_ensure(self) -> bool:
            assert self._online is not None, "online is not available"
            return self._online

        @property
        def online_or_none(self) -> bool | None:
            """Get the online status or return None when data was not fetched yet."""
            return self._online

        @property
        async def network_type(self) -> str:
            return (await self.basic_info).network_type

        @property
        def network_type_ensure(self) -> str:
            return self.basic_info_ensure.network_type

        @property
        def network_type_or_none(self) -> str | None:
            """Get the network type or return None when data was not fetched yet."""
            if self.is_basic_info_available:
                return self.basic_info_ensure.network_type
            return None

        @property
        async def chain_id(self) -> str:
            return (await self.basic_info).chain_id

        @property
        def chain_id_ensure(self) -> str:
            return self.basic_info_ensure.chain_id

        @property
        def chain_id_or_none(self) -> str | None:
            """Get the chain id or return None when data was not fetched yet."""
            if self.is_basic_info_available:
                return self.basic_info_ensure.chain_id
            return None

        def clear(self) -> None:
            self._basic_info = None

        async def update_dynamic_global_properties(
            self, new_data: DynamicGlobalProperties, *, update_only_when_definitely_newer_data: bool = True
        ) -> None:
            def set_data() -> None:
                basic_info.dynamic_global_properties = new_data

            def is_incoming_dgpo_data_newer() -> bool:
                return current_data.head_block_number < new_data.head_block_number

            basic_info = await self.basic_info
            current_data = basic_info.dynamic_global_properties

            if update_only_when_definitely_newer_data and not is_incoming_dgpo_data_newer():
                return

            set_data()

        def _set_online(self) -> None:
            self._online = True

        def _set_offline(self) -> None:
            self._online = False

        async def _fetch_basic_info(self) -> None:
            async with self._lock:
                if self._basic_info is None:
                    await self._node._sync_node_basic_info()

    def __init__(self, profile: Profile) -> None:
        self.__profile = profile
        self.__communication = Communication(timeout_total_secs=self.DEFAULT_TIMEOUT_TOTAL_SECONDS)
        self.api = Apis(self)
        self.cached = self.CachedData(self)
        self.__network_type = ""

    async def __aenter__(self) -> Self:
        await self.setup()
        return self

    async def __aexit__(
        self, _: type[BaseException] | None, __: BaseException | None, ___: TracebackType | None
    ) -> None:
        await self.teardown()

    async def setup(self) -> None:
        await self.__communication.setup()

    async def teardown(self) -> None:
        await self.__communication.teardown()

    def batch(self, *, delay_error_on_data_access: bool = False) -> _BatchNode:
        """
        In this mode all requests will be send as one request.

        Usage:

        with world.node.batch() as node:
            config = await node.api.database.get_config()
            dgpo = await node.api.database.get_dynamic_global_properties()
            # dgpo.time # this will raise Error
        dgpo.time # this is legit call
        """
        return _BatchNode(
            self, self.address, self.__communication, delay_error_on_data_access=delay_error_on_data_access
        )

    @contextmanager
    def modified_connection_details(
        self,
        max_attempts: int = Communication.DEFAULT_ATTEMPTS,
        timeout_total_secs: float = DEFAULT_TIMEOUT_TOTAL_SECONDS,
        pool_time_secs: float = Communication.DEFAULT_POOL_TIME_SECONDS,
    ) -> Iterator[None]:
        """Temporarily change connection details."""
        with self.__communication.modified_connection_details(max_attempts, timeout_total_secs, pool_time_secs):
            yield

    @property
    def address(self) -> Url:
        return self.__profile.node_address

    async def set_address(self, address: Url) -> None:
        self.__profile._set_node_address(address)
        self.cached.clear()

    def change_related_profile(self, profile: Profile) -> None:
        self.__profile = profile

    async def handle_request(
        self, request: JSONRPCRequest, *, expect_type: type[JSONRPCExpectResultT]
    ) -> JSONRPCExpectResultT:
        address = str(self.address)
        serialized_request = request.json(by_alias=True)

        try:
            data = await (await self.__communication.arequest(address, data=serialized_request)).json()
        except CommunicationError as error:
            if not error.is_response_available:
                self.cached._set_offline()
            raise

        endpoint = request.method
        response_model = get_response_model(expect_type, endpoint, **data)
        assert isinstance(
            response_model, JSONRPCResult
        ), f"Response  model is not JSONRPCResult, but {type(response_model)}"
        self.cached._set_online()
        return response_model.result  # type: ignore[no-any-return]

    @property
    async def chain_id(self) -> str:
        if chain_id_from_profile := self.__profile.chain_id:
            return chain_id_from_profile
        chain_id_from_node = await self.cached.chain_id
        self.__profile.set_chain_id(chain_id_from_node)
        return chain_id_from_node

    async def _sync_node_basic_info(self) -> None:
        try:
            self.cached._basic_info = await GetNodeBasicInfo(self).execute_with_result()
        except CommunicationError as error:
            if not error.is_response_available:
                self.cached._set_offline()
            raise
        else:
            self.cached._set_online()
