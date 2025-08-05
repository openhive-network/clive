from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Protocol, cast

import wax
from clive.__private.core.constants.precision import HIVE_PERCENT_PRECISION_DOT_PLACES
from clive.__private.core.decimal_conventer import DecimalConverter
from clive.__private.core.percent_conversions import hive_percent_to_percent
from clive.__private.models.schemas import convert_to_representation
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from decimal import Decimal

    from clive.__private.core.keys import PrivateKey, PublicKey
    from clive.__private.models import Asset, Transaction
    from clive.__private.models.schemas import OperationUnion, PriceFeed


class HpAPRProtocol(Protocol):
    """
    Simply pass gdpo, or object that provides required information needed to calculate Hp APR.

    Attributes:
        virtual_supply: The virtual supply of HIVE.
        total_vesting_fund_hive: The total vesting fund in HIVE.
    """

    @property
    def head_block_number(self) -> int: ...

    @property
    def vesting_reward_percent(self) -> int: ...

    virtual_supply: Asset.Hive
    total_vesting_fund_hive: Asset.Hive


class TotalVestingProtocol(Protocol):
    """
    Simply pass gdpo, or object that provides required information.

    Attributes:
        total_vesting_fund_hive: The total vesting fund in HIVE.
        total_vesting_shares: The total vesting shares.
    """

    total_vesting_fund_hive: Asset.Hive
    total_vesting_shares: Asset.Vests


class WaxOperationFailedError(CliveError):
    pass


def from_python_json_asset(result: wax.python_json_asset) -> Asset.AnyT:
    from clive.__private.models.asset import Asset

    asset_cls = Asset.resolve_nai(result.nai.decode())
    return asset_cls(amount=int(result.amount.decode()))


def to_python_json_asset(asset: Asset.AnyT) -> wax.python_json_asset:
    from clive.__private.models.asset import Asset, UnknownAssetTypeError

    match Asset.get_symbol(asset):
        case "HIVE" | "TESTS":
            return wax.hive(amount=int(asset.amount))
        case "HBD" | "TBD":
            return wax.hbd(amount=int(asset.amount))
        case "VESTS":
            return wax.vests(amount=int(asset.amount))
        case _:
            raise UnknownAssetTypeError(asset.nai)


def __validate_wax_response(response: wax.python_result) -> None:
    if response.status == wax.python_error_code.fail:
        raise WaxOperationFailedError(response.exception_message.decode())


def __as_binary_json(item: OperationUnion | Transaction) -> bytes:
    from clive.__private.models import Transaction

    if not isinstance(item, Transaction):
        item = convert_to_representation(item)

    return item.json().encode()


def validate_transaction(transaction: Transaction) -> None:
    return __validate_wax_response(wax.validate_transaction(__as_binary_json(transaction)))


def validate_operation(operation: OperationUnion) -> None:
    return __validate_wax_response(wax.validate_operation(__as_binary_json(operation)))


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


def deserialize_transaction(transaction: bytes) -> Transaction:
    from clive.__private.models import Transaction

    result = wax.deserialize_transaction(transaction)
    __validate_wax_response(result)
    return Transaction.parse_raw(result.result.decode())


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
    return datetime.datetime.fromtimestamp(int(result.result.decode()), tz=datetime.UTC)


def calculate_current_manabar_value(now: int, max_mana: int, current_mana: int, last_update_time: int) -> int:
    result = wax.calculate_current_manabar_value(
        now=now, max_mana=max_mana, current_mana=current_mana, last_update_time=last_update_time
    )
    __validate_wax_response(result)
    return int(result.result.decode())


def general_asset(asset_num: int, amount: int) -> Asset.AnyT:
    return from_python_json_asset(wax.general_asset(asset_num=asset_num, amount=amount))


def get_tapos_data(block_id: str) -> wax.python_ref_block_data:
    return wax.get_tapos_data(block_id.encode())


def hive(amount: int) -> Asset.Hive:
    return cast("Asset.Hive", from_python_json_asset(wax.hive(amount)))


def hbd(amount: int) -> Asset.Hbd:
    return cast("Asset.Hbd", from_python_json_asset(wax.hbd(amount)))


def vests(amount: int) -> Asset.Vests:
    return cast("Asset.Vests", from_python_json_asset(wax.vests(amount)))


def calculate_hp_apr(data: HpAPRProtocol) -> Decimal:
    result = wax.calculate_hp_apr(
        head_block_num=data.head_block_number,
        vesting_reward_percent=data.vesting_reward_percent,
        virtual_supply=to_python_json_asset(data.virtual_supply),
        total_vesting_fund_hive=to_python_json_asset(data.total_vesting_fund_hive),
    )
    __validate_wax_response(result)
    return DecimalConverter.convert(result.result.decode(), precision=HIVE_PERCENT_PRECISION_DOT_PLACES)


def calculate_hbd_to_hive(_hbd: Asset.Hbd, current_price_feed: PriceFeed) -> Asset.Hive:
    result = wax.calculate_hbd_to_hive(
        hbd=to_python_json_asset(_hbd),
        base=to_python_json_asset(current_price_feed.base),
        quote=to_python_json_asset(current_price_feed.quote),
    )
    return cast("Asset.Hive", from_python_json_asset(result))


def calculate_vests_to_hp(_vests: int | Asset.Vests, data: TotalVestingProtocol) -> Asset.Hive:
    vests_json_asset = wax.vests(_vests) if isinstance(_vests, int) else to_python_json_asset(_vests)
    result = wax.calculate_vests_to_hp(
        vests=vests_json_asset,
        total_vesting_fund_hive=to_python_json_asset(data.total_vesting_fund_hive),
        total_vesting_shares=to_python_json_asset(data.total_vesting_shares),
    )
    return cast("Asset.Hive", from_python_json_asset(result))


def calculate_hp_to_vests(_hive: Asset.Hive, data: TotalVestingProtocol) -> Asset.Vests:
    result = wax.calculate_hp_to_vests(
        hive=to_python_json_asset(_hive),
        total_vesting_fund_hive=to_python_json_asset(data.total_vesting_fund_hive),
        total_vesting_shares=to_python_json_asset(data.total_vesting_shares),
    )
    return cast("Asset.Vests", from_python_json_asset(result))


def calculate_current_inflation_rate(head_block_num: int) -> Decimal:
    result = wax.calculate_inflation_rate_for_block(head_block_num)
    __validate_wax_response(result)
    return hive_percent_to_percent(result.result.decode())


def calculate_witness_votes_hp(votes: int, data: TotalVestingProtocol) -> Asset.Hive:
    result = wax.calculate_witness_votes_hp(
        votes=votes,
        total_vesting_fund_hive=to_python_json_asset(data.total_vesting_fund_hive),
        total_vesting_shares=to_python_json_asset(data.total_vesting_shares),
    )
    return cast("Asset.Hive", from_python_json_asset(result))


def generate_password_based_private_key(
    password: str, role: str = "memo", account_name: str = "anything"
) -> PrivateKey:
    from clive.__private.core.keys import PrivateKey

    result = wax.generate_password_based_private_key(account_name.encode(), role.encode(), password.encode())
    return PrivateKey(value=result.wif_private_key.decode())
