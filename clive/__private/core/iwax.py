from __future__ import annotations

import datetime
import json
from typing import TYPE_CHECKING, Any

import wax
from clive.__private.core.communication import CustomJSONEncoder
from clive.exceptions import CliveError
from clive.models import Transaction
from clive.models.convert_to_representation import convert_to_representation

if TYPE_CHECKING:
    from clive.__private.core.keys import PrivateKey, PublicKey
    from clive.models import Operation


class WaxOperationFailedError(CliveError):
    pass


def __validate_wax_response(response: wax.python_result) -> None:
    if response.status == wax.python_error_code.fail:
        raise WaxOperationFailedError(response.exception_message.decode())


def __as_binary_json(item: Operation | Transaction | dict[str, Any]) -> bytes:
    if isinstance(item, dict):
        return json.dumps(item, cls=CustomJSONEncoder).encode()

    if not isinstance(item, Transaction):
        item = convert_to_representation(item)

    return item.json(by_alias=True).encode()


def validate_transaction(transaction: Transaction) -> None:
    return __validate_wax_response(wax.validate_transaction(__as_binary_json(transaction)))


def validate_operation(operation: Operation) -> None:
    return __validate_wax_response(wax.validate_operation(__as_binary_json(operation)))


def validate_proto_transaction(transaction: dict[str, Any]) -> None:
    return __validate_wax_response(wax.validate_proto_transaction(__as_binary_json(transaction)))


def validate_proto_operation(operation: dict[str, Any]) -> None:
    return __validate_wax_response(wax.validate_proto_operation(__as_binary_json(operation)))


def calculate_sig_digest(transaction: Transaction, chain_id: str) -> str:
    result = wax.calculate_sig_digest(__as_binary_json(transaction), chain_id.encode())
    __validate_wax_response(result)
    return result.result.decode()


def calculate_transaction_id(transaction: Transaction) -> str:
    result = wax.calculate_transaction_id(__as_binary_json(transaction))
    __validate_wax_response(result)
    return result.result.decode()


def serialize_transaction(transaction: Transaction) -> bytes:
    result = wax.serialize_transaction(__as_binary_json(transaction))
    __validate_wax_response(result)
    return result.result


def calculate_public_key(wif: str) -> PublicKey:
    from clive.__private.core.keys import PublicKey

    result = wax.calculate_public_key(wif.encode())
    __validate_wax_response(result)
    return PublicKey(value=result.result.decode())


def generate_private_key() -> PrivateKey:
    from clive.__private.core.keys import PrivateKey

    result = wax.generate_private_key()
    __validate_wax_response(result)
    return PrivateKey(value=result.result.decode())


def calculate_manabar_full_regeneration_time(
    now: int, max_mana: int, current_mana: int, last_update_time: int
) -> datetime.datetime:
    result = wax.calculate_manabar_full_regeneration_time(
        now=now, max_mana=max_mana, current_mana=current_mana, last_update_time=last_update_time
    )
    __validate_wax_response(result)
    return datetime.datetime.utcfromtimestamp(int(result.result.decode())).replace(tzinfo=datetime.timezone.utc)


def calculate_current_manabar_value(now: int, max_mana: int, current_mana: int, last_update_time: int) -> int:
    result = wax.calculate_current_manabar_value(
        now=now, max_mana=max_mana, current_mana=current_mana, last_update_time=last_update_time
    )
    __validate_wax_response(result)
    return int(result.result.decode())


def general_asset(asset_num: int, amount: int) -> wax.python_json_asset:
    return wax.general_asset(asset_num=asset_num, amount=amount)


def hive(amount: int) -> wax.python_json_asset:
    return wax.hive(amount=amount)


def hbd(amount: int) -> wax.python_json_asset:
    return wax.hbd(amount=amount)


def vests(amount: int) -> wax.python_json_asset:
    return wax.vests(amount=amount)
