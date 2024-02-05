from __future__ import annotations

from datetime import timedelta, datetime
from typing import TYPE_CHECKING

import wax
from schemas.fields.hive_int import HiveInt
from schemas.operations.representations import HF26Representation
from schemas.transaction import Transaction

if TYPE_CHECKING:
    from schemas.apis.database_api import GetDynamicGlobalProperties
    from schemas.operations import AnyOperation


class SimpleTransaction(Transaction):
    def add_operation(self, op: AnyOperation) -> None:
        self.operations.append(HF26Representation(type=op.get_name_with_suffix(), value=op))


def get_tapos_data(block_id: str) -> wax.python_ref_block_data:
    return wax.get_tapos_data(block_id.encode())  # type: ignore[no-any-return]


def generate_transaction_template(
    gdpo: GetDynamicGlobalProperties,
    time_offset: datetime
) -> SimpleTransaction:
    # get dynamic global properties
    # Fixme: after add block_log_util methods to test_tools
    # block_id = gdpo.head_block_id
    block_id: str = "000001f9b430c592320c58eb2dd659f42d09bf70"


    # set header
    tapos_data = get_tapos_data(block_id)
    ref_block_num = tapos_data.ref_block_num
    ref_block_prefix = tapos_data.ref_block_prefix

    assert ref_block_num >= 0, f"ref_block_num value `{ref_block_num}` is invalid`"
    assert ref_block_prefix > 0, f"ref_block_prefix value `{ref_block_prefix}` is invalid`"

    return SimpleTransaction(
        ref_block_num=HiveInt(ref_block_num),
        ref_block_prefix=HiveInt(ref_block_prefix),
        expiration=gdpo.time + timedelta(seconds=time_offset) + timedelta(minutes=59),
        extensions=[],
        signatures=[],
        operations=[],
    )
