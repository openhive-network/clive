from __future__ import annotations

import asyncio
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING

import beekeepy.exceptions as bke

from clive.__private.core.commands.data_retrieval.get_node_basic_info import GetNodeBasicInfo, NodeBasicInfoData
from clive.__private.settings import safe_settings
from wax.helpy import AsyncHived

if TYPE_CHECKING:
    from collections.abc import Iterator

    from beekeepy.interfaces import HttpUrl

    from clive.__private.core.profile import Profile
    from clive.__private.models.schemas import Config, DynamicGlobalProperties, Version


class Node(AsyncHived):
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
            except bke.CommunicationError as error:
                if error.response is None:
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
        self.cached = self.CachedData(self)
        super().__init__(settings=safe_settings.node.settings_factory(self.http_endpoint))

    @property
    def http_endpoint(self) -> HttpUrl:
        """Return endpoint where handle is connected to."""
        return self.__profile.node_address

    @http_endpoint.setter
    def http_endpoint(self, address: HttpUrl) -> None:
        """
        Override because of mypy: Read-only property cannot override read-write property  [misc].

        Args:
            address: New address to set.

        Raises:
            NotImplementedError: This method is not intended for usage.
        """
        raise NotImplementedError("use set_address method!")

    @contextmanager
    def modified_connection_details(
        self,
        max_attempts: int | None = None,
        timeout_total_secs: float | None = None,
    ) -> Iterator[None]:
        """
        Temporarily change connection details.

        Args:
            max_attempts: Maximum number of retries for connection attempts.
            timeout_total_secs: Total timeout in seconds for the connection.
        """
        with self.restore_settings():
            self.settings.max_retries = max_attempts or self.settings.max_retries
            self.settings.timeout = timedelta(seconds=(timeout_total_secs or self.settings.timeout.seconds))
            yield

    async def _set_address(self, address: HttpUrl) -> None:
        """
        Set the node address.

        It is marked as not intended for usage because you rather should use world.set_address
        instead (it also sets wax interface)
        """
        self.__profile._set_node_address(address)
        self.cached.clear()

    def change_related_profile(self, profile: Profile) -> None:
        self.__profile = profile

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
        except bke.CommunicationError as error:
            if error.response is None:
                self.cached._set_offline()
            raise
        else:
            self.cached._set_online()
