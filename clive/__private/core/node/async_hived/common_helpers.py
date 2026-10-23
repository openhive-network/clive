from __future__ import annotations

from typing import TYPE_CHECKING

from hiveio_api.database_api import GetDynamicGlobalPropertiesResponse

if TYPE_CHECKING:
    from hiveio_api import HiveDateTime
    from hiveio_api.database_api import GetVersionResponse


class HiveHandleCommonHelpers:
    type GetDynamicGlobalPropertiesT = GetDynamicGlobalPropertiesResponse

    def _get_last_block_number(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> int:
        return dynamic_global_properties.head_block_number

    def _get_last_irreversible_block_number(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> int:
        return dynamic_global_properties.last_irreversible_block_num

    def _get_head_block_time(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> HiveDateTime:
        return dynamic_global_properties.time

    def _get_current_witness(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> str:
        return dynamic_global_properties.current_witness

    def _hived_target_service_name(self) -> str:
        return "hived"

    def _extract_network_type(self, get_version: GetVersionResponse) -> str:
        return get_version.node_type

    def _assert_non_negative_amount_of_blocks(self, amount_of_blocks: int) -> None:
        assert amount_of_blocks > 0, "Can't wait for negative or zero amount of blocks"
