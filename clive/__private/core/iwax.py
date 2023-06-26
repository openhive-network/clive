from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import wax
from clive.__private.core.keys import PrivateKey, PublicKey
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from clive.models import Operation, Transaction


class WaxOperationFailedError(CliveError):
    pass


def __validate_wax_response(response: wax.python_result) -> bool:
    if response.status == wax.python_error_code.fail:
        raise WaxOperationFailedError(response.exception_message.decode())
    return True


def __as_binary_json(item: Operation | Transaction) -> bytes:
    return item.json(by_alias=True).encode()


def validate_transaction(transaction: Transaction) -> bool:
    return __validate_wax_response(wax.validate_transaction(__as_binary_json(transaction)))


def validate_operation(operation: Operation) -> bool:
    return __validate_wax_response(wax.validate_operation(__as_binary_json(operation)))


def calculate_digest(transaction: Transaction, chain_id: str) -> str:
    result = wax.calculate_digest(__as_binary_json(transaction), chain_id.encode())
    __validate_wax_response(result)
    return result.result.decode()


def serialize_transaction(transaction: Transaction) -> bytes:
    result = wax.serialize_transaction(__as_binary_json(transaction))
    __validate_wax_response(result)
    return result.result


def calculate_public_key(wif: str) -> PublicKey:
    result = wax.calculate_public_key(wif.encode())
    __validate_wax_response(result)
    return PublicKey(value=result.result.decode())


def generate_private_key() -> PrivateKey:
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
    return datetime.datetime.utcfromtimestamp(int(result.result.decode()))


def calculate_current_manabar_value(now: int, max_mana: int, current_mana: int, last_update_time: int) -> int:
    result = wax.calculate_current_manabar_value(
        now=now, max_mana=max_mana, current_mana=current_mana, last_update_time=last_update_time
    )
    __validate_wax_response(result)
    return int(result.result.decode())
