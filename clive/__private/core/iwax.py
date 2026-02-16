from __future__ import annotations

import datetime
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, Protocol, cast

import wax
from clive.__private.core.constants.precision import HIVE_PERCENT_PRECISION_DOT_PLACES
from clive.__private.core.decimal_conventer import DecimalConverter
from clive.__private.core.percent_conversions import hive_percent_to_percent
from clive.exceptions import CliveError

if TYPE_CHECKING:
    from decimal import Decimal

    from clive.__private.core.keys import PrivateKey, PublicKey
    from clive.__private.models.asset import Asset
    from clive.__private.models.schemas import Account, Authority, OperationUnion, PriceFeed
    from clive.__private.models.transaction import Transaction
    from wax.models.authority import WaxAuthorities, WaxAuthority
    from wax.wax_result import python_encrypted_memo


def cast_hiveint_args[F: Callable[..., Any]](func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        from clive.__private.models.schemas import HiveInt  # noqa: PLC0415

        def hiveint_to_int(value: Any) -> Any:  # noqa: ANN401
            return int(value) if isinstance(value, HiveInt) else value

        new_args = tuple(hiveint_to_int(arg) for arg in args)
        new_kwargs = {k: hiveint_to_int(v) for k, v in kwargs.items()}

        return func(*new_args, **new_kwargs)

    return cast("F", wrapper)


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
    from clive.__private.models.asset import Asset  # noqa: PLC0415

    asset_cls = Asset.resolve_nai(result.nai)
    return asset_cls(amount=int(result.amount))


def to_python_json_asset(asset: Asset.AnyT) -> wax.python_json_asset:
    from clive.__private.models.asset import Asset, UnknownAssetTypeError  # noqa: PLC0415

    match Asset.get_symbol(asset):
        case "HIVE" | "TESTS":
            return wax.hive(amount=int(asset.amount))
        case "HBD" | "TBD":
            return wax.hbd(amount=int(asset.amount))
        case "VESTS":
            return wax.vests(amount=int(asset.amount))
        case _:
            raise UnknownAssetTypeError(asset.nai())


def __validate_wax_response(response: wax.python_result) -> None:
    if response.status == wax.python_error_code.fail:
        raise WaxOperationFailedError(response.exception_message)


def __as_binary_json(item: OperationUnion | Transaction) -> str:
    from clive.__private.models.schemas import convert_to_representation  # noqa: PLC0415
    from clive.__private.models.transaction import Transaction  # noqa: PLC0415

    to_serialize = item if isinstance(item, Transaction) else convert_to_representation(item)
    return to_serialize.json()


def validate_transaction(transaction: Transaction) -> None:
    return __validate_wax_response(wax.validate_transaction(__as_binary_json(transaction)))


def validate_operation(operation: OperationUnion) -> None:
    return __validate_wax_response(wax.validate_operation(__as_binary_json(operation)))


def calculate_sig_digest(transaction: Transaction, chain_id: str) -> str:
    result = wax.calculate_sig_digest(__as_binary_json(transaction), chain_id)
    __validate_wax_response(result)
    return result.result


def calculate_transaction_id(transaction: Transaction) -> str:
    result = wax.calculate_transaction_id(__as_binary_json(transaction))
    __validate_wax_response(result)
    return result.result


def serialize_transaction(transaction: Transaction) -> bytes:
    result = wax.serialize_transaction(__as_binary_json(transaction))
    __validate_wax_response(result)
    return result.result.encode()


def deserialize_transaction(transaction: bytes) -> Transaction:
    from clive.__private.models.transaction import Transaction  # noqa: PLC0415

    result = wax.deserialize_transaction(transaction.decode())
    __validate_wax_response(result)
    return Transaction.parse_raw(result.result)


def calculate_public_key(wif: str) -> PublicKey:
    from clive.__private.core.keys import PublicKey  # noqa: PLC0415

    result = wax.calculate_public_key(wif)
    __validate_wax_response(result)
    return PublicKey(value=result.result)


def generate_private_key() -> PrivateKey:
    from clive.__private.core.keys import PrivateKey  # noqa: PLC0415

    result = wax.generate_private_key()
    __validate_wax_response(result)
    return PrivateKey(value=result.result)


@cast_hiveint_args
def calculate_manabar_full_regeneration_time(
    now: int, max_mana: int, current_mana: int, last_update_time: int
) -> datetime.datetime:
    result = wax.calculate_manabar_full_regeneration_time(
        now=now, max_mana=max_mana, current_mana=current_mana, last_update_time=last_update_time
    )
    __validate_wax_response(result)
    return datetime.datetime.fromtimestamp(int(result.result), tz=datetime.UTC)


@cast_hiveint_args
def calculate_current_manabar_value(now: int, max_mana: int, current_mana: int, last_update_time: int) -> int:
    result = wax.calculate_current_manabar_value(
        now=now, max_mana=max_mana, current_mana=current_mana, last_update_time=last_update_time
    )
    __validate_wax_response(result)
    return int(result.result)


@cast_hiveint_args
def general_asset(asset_num: int, amount: int) -> Asset.AnyT:
    return from_python_json_asset(wax.general_asset(asset_num=asset_num, amount=amount))


def get_tapos_data(block_id: str) -> wax.python_ref_block_data:
    return wax.get_tapos_data(block_id)


@cast_hiveint_args
def hive(amount: int) -> Asset.Hive:
    return cast("Asset.Hive", from_python_json_asset(wax.hive(amount)))


@cast_hiveint_args
def hbd(amount: int) -> Asset.Hbd:
    return cast("Asset.Hbd", from_python_json_asset(wax.hbd(amount)))


@cast_hiveint_args
def vests(amount: int) -> Asset.Vests:
    return cast("Asset.Vests", from_python_json_asset(wax.vests(amount)))


def calculate_hp_apr(data: HpAPRProtocol) -> Decimal:
    result = wax.calculate_hp_apr(
        head_block_num=int(data.head_block_number),
        vesting_reward_percent=int(data.vesting_reward_percent),
        virtual_supply=to_python_json_asset(data.virtual_supply),
        total_vesting_fund_hive=to_python_json_asset(data.total_vesting_fund_hive),
    )
    __validate_wax_response(result)
    return DecimalConverter.convert(result.result, precision=HIVE_PERCENT_PRECISION_DOT_PLACES)


def calculate_hbd_to_hive(_hbd: Asset.Hbd, current_price_feed: PriceFeed) -> Asset.Hive:
    result = wax.calculate_hbd_to_hive(
        hbd=to_python_json_asset(_hbd),
        base=to_python_json_asset(current_price_feed.base),
        quote=to_python_json_asset(current_price_feed.quote),
    )
    return cast("Asset.Hive", from_python_json_asset(result))


@cast_hiveint_args
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


@cast_hiveint_args
def calculate_current_inflation_rate(head_block_num: int) -> Decimal:
    result = wax.calculate_inflation_rate_for_block(head_block_num)
    __validate_wax_response(result)
    return hive_percent_to_percent(result.result)


@cast_hiveint_args
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
    from clive.__private.core.keys import PrivateKey  # noqa: PLC0415

    result = wax.generate_password_based_private_key(account_name, role, password)
    return PrivateKey(value=result.wif_private_key)


def suggest_brain_key() -> str:
    result = wax.suggest_brain_key()
    return result.brain_key


def encode_encrypted_memo(encrypted_content: str, main_encryption_key: str, other_encryption_key: str = "") -> str:
    return wax.encode_encrypted_memo(encrypted_content, main_encryption_key, other_encryption_key)


def decode_encrypted_memo(encoded_memo: str) -> python_encrypted_memo:
    return wax.decode_encrypted_memo(encoded_memo)


def transaction_get_impacted_accounts(transaction: Transaction) -> list[str]:
    return wax.transaction_get_impacted_accounts(__as_binary_json(transaction))


def collect_signing_keys(
    transaction: Transaction,
    retrieve_authorities: Callable[[list[str]], dict[str, wax.python_authorities]],
) -> list[str]:
    return wax.collect_signing_keys(__as_binary_json(transaction), retrieve_authorities)


def minimize_required_signatures(  # noqa: PLR0913
    signed_transaction: Transaction,
    chain_id: str,
    available_keys: list[str],
    authorities_map: dict[str, wax.python_authorities],
    get_witness_key: Callable[[str], str],
    *,
    max_recursion: int | None = None,
    max_membership: int | None = None,
    max_account_auths: int | None = None,
) -> list[str]:
    data = wax.python_minimize_required_signatures_data(
        chain_id=chain_id,
        available_keys=available_keys,
        authorities_map=authorities_map,
        get_witness_key=get_witness_key,
        max_recursion=max_recursion,
        max_membership=max_membership,
        max_account_auths=max_account_auths,
    )
    return wax.minimize_required_signatures(__as_binary_json(signed_transaction), data)


def convert_wax_authorities_to_python_authorities(wax_auths: WaxAuthorities) -> wax.python_authorities:
    def _convert(auth: WaxAuthority | None) -> wax.python_authority:
        if auth is None:
            return wax.python_authority(weight_threshold=0, account_auths={}, key_auths={})
        return wax.python_authority(
            weight_threshold=auth.weight_threshold,
            account_auths=dict(auth.account_auths.items()),
            key_auths=dict(auth.key_auths.items()),
        )

    return wax.python_authorities(
        owner=_convert(wax_auths.owner),
        active=_convert(wax_auths.active),
        posting=_convert(wax_auths.posting),
    )


def convert_schemas_account_to_python_authorities(account: Account) -> wax.python_authorities:
    def _convert_authority(authority: Authority) -> wax.python_authority:
        return wax.python_authority(
            weight_threshold=int(authority.weight_threshold),
            account_auths={name: int(weight) for name, weight in authority.account_auths},
            key_auths={key: int(weight) for key, weight in authority.key_auths},
        )

    return wax.python_authorities(
        owner=_convert_authority(account.owner),
        active=_convert_authority(account.active),
        posting=_convert_authority(account.posting),
    )
