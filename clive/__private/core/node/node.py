from __future__ import annotations

from abc import abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

from clive.__private.config import settings
from clive.__private.core.commands.data_retrieval.get_config import GetConfig
from clive.__private.core.communication import Communication
from clive.__private.core.node.api.apis import Apis
from clive.exceptions import CliveError, CommunicationError
from schemas.jsonrpc import ExpectResultT, JSONRPCRequest, JSONRPCResult, get_response_model

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType

    from typing_extensions import Self

    from clive.__private.core.profile_data import ProfileData
    from clive.core.url import Url
    from clive.models.aliased import Config


class BatchRequestError(CliveError):
    pass


class NothingToSendError(BatchRequestError):
    pass


class ResponseNotReadyError(BatchRequestError):
    pass


class BaseNode:
    @abstractmethod
    async def handle_request(self, request: JSONRPCRequest, *, expect_type: type[ExpectResultT]) -> ExpectResultT: ...


class _DelayedResponseWrapper:
    def __init__(self, url: Url, request: str, expected_type: type[ExpectResultT]) -> None:
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
        super().__setattr__("_response", get_response_model(expected_type, **kwargs))

    def _set_exception(self, exception: Exception) -> None:
        super().__setattr__("_exception", exception)


@dataclass(kw_only=True)
class _BatchRequestResponseItem:
    request: str
    delayed_result: _DelayedResponseWrapper


class _BatchNode(BaseNode):
    def __init__(self, url: Url, communication: Communication, *, delay_error_on_data_access: bool = False) -> None:
        self.__url = url
        self.__communication = communication
        self.__delay_error_on_data_access = delay_error_on_data_access

        self.__batch: list[_BatchRequestResponseItem] = []
        self.api = Apis(self)

    async def handle_request(self, request: JSONRPCRequest, *, expect_type: type[ExpectResultT]) -> ExpectResultT:
        request.id_ = len(self.__batch)
        serialized_request = request.json(by_alias=True)
        delayed_result = _DelayedResponseWrapper(url=self.__url, request=serialized_request, expected_type=expect_type)
        self.__batch.append(_BatchRequestResponseItem(request=serialized_request, delayed_result=delayed_result))
        return delayed_result  # type: ignore[return-value]

    async def __evaluate(self) -> None:
        num_of_requests = len(self.__batch)
        query = "[" + ",".join([x.request for x in self.__batch]) + "]"

        try:
            responses: list[dict[str, Any]] = await (
                await self.__communication.arequest(url=self.__url.as_string(), data=query)
            ).json()
        except CommunicationError as error:
            responses_from_error = error.get_response()

            # There is no response available, set this exception on all delayed results.
            if responses_from_error is None:
                for request_id in range(num_of_requests):
                    self.__get_batch_delayed_result(request_id)._set_exception(error)

                if not self.__delay_error_on_data_access:
                    raise
                return

            message = f"Invalid error response format: expected list, got {type(responses_from_error)}"
            assert isinstance(responses_from_error, list), message
            assert len(responses_from_error) == len(self.__batch), "Invalid amount of responses_from_error"

            # Some of the responses might be errors, some might be good - set them on delayed results.
            for response in responses_from_error:
                request_id = int(response["id"])
                if "error" in response:
                    # creating a new instance so other responses won't be included in the error
                    new_error = CommunicationError(
                        url=error.url,
                        request=self.__batch[request_id].request,
                        response=response,
                    )
                    self.__get_batch_delayed_result(request_id)._set_exception(new_error)
                else:
                    self.__get_batch_delayed_result(request_id)._set_response(**response)

            if not self.__delay_error_on_data_access:
                raise
        else:
            assert len(responses) == len(self.__batch), "Invalid amount of responses"
            for response in responses:
                request_id = int(response["id"])
                self.__get_batch_delayed_result(request_id)._set_response(**response)

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
    DEFAULT_TIMEOUT_TOTAL_SECONDS: Final[float] = settings.get(
        "node.communication_total_timeout_secs", Communication.DEFAULT_TIMEOUT_TOTAL_SECONDS
    )

    def __init__(self, profile_data: ProfileData) -> None:
        self.__profile_data = profile_data
        self.__communication = Communication(timeout_secs=self.DEFAULT_TIMEOUT_TOTAL_SECONDS)
        self.api = Apis(self)
        self.__network_type = ""
        self._node_config: Config | None = None

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
        return _BatchNode(self.address, self.__communication, delay_error_on_data_access=delay_error_on_data_access)

    @contextmanager
    def modified_connection_details(
        self,
        max_attempts: int = Communication.DEFAULT_ATTEMPTS,
        timeout_secs: float = DEFAULT_TIMEOUT_TOTAL_SECONDS,
        pool_time_secs: float = Communication.DEFAULT_POOL_TIME_SECONDS,
    ) -> Iterator[None]:
        """Temporarily change connection details."""
        with self.__communication.modified_connection_details(max_attempts, timeout_secs, pool_time_secs):
            yield

    @property
    async def network_type(self) -> str:
        if not self.__network_type:
            await self.__sync_node_version()
        return self.__network_type

    @property
    def address(self) -> Url:
        return self.__profile_data.node_address

    async def set_address(self, address: Url) -> None:
        self.__profile_data._set_node_address(address)
        self._node_config = None
        await self.__sync_node_version()

    async def handle_request(self, request: JSONRPCRequest, *, expect_type: type[ExpectResultT]) -> ExpectResultT:
        address = str(self.address)
        serialized_request = request.json(by_alias=True)
        response = await self.__communication.arequest(address, data=serialized_request)
        data = await response.json()
        response_model = get_response_model(expect_type, **data)
        if isinstance(response_model, JSONRPCResult):
            return response_model.result
        raise CommunicationError(address, serialized_request, data)

    @property
    async def chain_id(self) -> str:
        if chain_id_from_profile := self.__profile_data.chain_id:
            return chain_id_from_profile
        chain_id_from_node = (await self.node_config).HIVE_CHAIN_ID
        self.__profile_data.set_chain_id(chain_id_from_node)
        return chain_id_from_node

    async def __sync_node_version(self) -> None:
        if self.address:
            try:
                self.__network_type = (await self.api.database_api.get_version()).node_type
            except CommunicationError:
                self.__network_type = "no connection"

    @property
    async def node_config(self) -> Config:
        if self._node_config is None:
            self._node_config = await GetConfig(node=self).execute_with_result()
        assert self._node_config is not None, "could not get config"
        return self._node_config
