from __future__ import annotations

from beekeepy.handle.remote import AbstractAsyncApi

from hiveio_api import block_api


class BlockApi(AbstractAsyncApi):
    api = AbstractAsyncApi.endpoint_jsonrpc

    @api
    async def get_block_header(self, *, block_num: int) -> block_api.GetBlockHeaderResponse:
        raise NotImplementedError

    @api
    async def get_block(self, *, block_num: int) -> block_api.GetBlockResponse:
        raise NotImplementedError

    @api
    async def get_block_range(self, starting_block_num: int, count: int) -> block_api.GetBlockRangeResponse:
        raise NotImplementedError
