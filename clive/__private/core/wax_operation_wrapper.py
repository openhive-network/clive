from __future__ import annotations

from typing import TYPE_CHECKING, Self, TypeVar, overload

from clive.__private.core.percent_conversions import percent_to_hive_percent
from clive.__private.models.schemas import AccountName, OperationUnion
from clive.exceptions import WrongTypeError

if TYPE_CHECKING:
    from decimal import Decimal

    import wax
    from clive.__private.core.keys import PublicKey
    from clive.__private.models.asset import Asset
    from wax._private.operation_base import OperationBase as WaxOperationBase


OperationExpectType = TypeVar("OperationExpectType", bound=OperationUnion)


class WaxOperationWrapper:
    def __init__(self, wax_operation: WaxOperationBase) -> None:
        self._wax_operation = wax_operation

    @classmethod
    def create_witness_set_properties(  # noqa: PLR0913
        cls,
        *,
        owner: str,
        key: str | PublicKey,
        new_signing_key: str | PublicKey | None = None,
        account_creation_fee: Asset.Hive | None = None,
        url: str | None = None,
        hbd_exchange_rate: Asset.Hbd | None = None,
        maximum_block_size: int | None = None,
        hbd_interest_rate: Decimal | None = None,
        account_subsidy_budget: int | None = None,
        account_subsidy_decay: int | None = None,
    ) -> Self:
        from clive.__private.core.keys import PublicKey  # noqa: PLC0415
        from clive.__private.models.asset import Asset  # noqa: PLC0415
        from wax.complex_operations.witness_set_properties import (  # noqa: PLC0415
            HbdExchangeRate,
            WitnessSetProperties,
            WitnessSetPropertiesData,
        )

        def key_string(input_key: str | PublicKey) -> str:
            return PublicKey(value=input_key).value if isinstance(input_key, str) else input_key.value

        return cls(
            WitnessSetProperties(
                data=WitnessSetPropertiesData(
                    owner=AccountName(owner),
                    witness_signing_key=key_string(key),
                    new_signing_key=key_string(new_signing_key) if new_signing_key is not None else None,
                    account_creation_fee=account_creation_fee.as_serialized_nai()
                    if account_creation_fee is not None
                    else None,
                    url=url,
                    hbd_exchange_rate=HbdExchangeRate(
                        base=hbd_exchange_rate.as_serialized_nai(),
                        quote=Asset.hive(1).as_serialized_nai(),
                    )
                    if hbd_exchange_rate
                    else None,
                    maximum_block_size=maximum_block_size,
                    hbd_interest_rate=percent_to_hive_percent(hbd_interest_rate) if hbd_interest_rate else None,
                    account_subsidy_budget=account_subsidy_budget,
                    account_subsidy_decay=account_subsidy_decay,
                )
            )
        )

    @overload
    def to_schemas(
        self, wax_interface: wax.IHiveChainInterface, expect_type: type[OperationExpectType]
    ) -> OperationExpectType: ...

    @overload
    def to_schemas(self, wax_interface: wax.IHiveChainInterface, expect_type: None = None) -> OperationUnion: ...

    def to_schemas(
        self, wax_interface: wax.IHiveChainInterface, expect_type: type[OperationExpectType] | None = None
    ) -> OperationExpectType:
        from clive.__private.models.transaction import Transaction  # noqa: PLC0415

        # We must specify tapos now, this will be changed with resolving issue https://gitlab.syncad.com/hive/wax/-/issues/128
        wax_transaction = wax_interface.create_transaction_with_tapos("0")

        proto_operations = list(self._wax_operation.finalize(wax_interface))
        assert len(proto_operations) == 1, "A single proto operation was expected when finalizing"
        wax_transaction.push_operation(proto_operations[0])

        schemas_transaction = Transaction.parse_raw(wax_transaction.to_api_json())
        schemas_operation = schemas_transaction.operations_models[0]

        if expect_type and not isinstance(schemas_operation, expect_type):
            raise WrongTypeError(expect_type, type(schemas_operation))

        return schemas_operation  # type: ignore[return-value]
