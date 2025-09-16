from __future__ import annotations

from clive.__private.core.iwax import to_python_json_asset
from schemas.fields.compound import WitnessProps
from schemas.operations.witness_set_properties_operation import (
    WitnessSetPropertiesOperation,
    WitnessSetPropertiesOperationFactory,
)
from wax import python_price, serialize_witness_set_properties
from wax.complex_operations.witness_set_properties import WitnessSetProperties, WitnessSetPropertiesData

schema_props = WitnessProps(
    # account_creation_fee=AssetHive(100),
    # maximum_block_size=1,
    # hbd_exchange_rate=HbdExchangeRate(AssetHbd(100), AssetHive(100)),
    # account_subsidy_budget=1,
    # account_subsidy_decay=1,
    # url="test",
    # new_signing_key="STM8PFEEhF9g3PMZu9mu9vso56bzP6i4aMYM73aWL8CkcKi4LEGLR"
)

schema_op_factory = WitnessSetPropertiesOperationFactory(owner="mee", props=schema_props)
# print(schema_op_factory.json(indent=4))

shema_op_props = schema_op_factory.props


wax_op = WitnessSetProperties(
    WitnessSetPropertiesData(
        owner=schema_op_factory.owner,
        witness_signing_key="STM8PFEEhF9g3PMZu9mu9vso56bzP6i4aMYM73aWL8CkcKi4LEGLR",
        new_signing_key=shema_op_props.new_signing_key,
        account_creation_fee=shema_op_props.account_creation_fee,  # type: ignore # doesn't matter, won't be set anyway
        url=shema_op_props.url,
        hbd_exchange_rate=shema_op_props.hbd_exchange_rate,  # type: ignore # doesn't matter, won't be set anyway
        maximum_block_size=shema_op_props.maximum_block_size,
        hbd_interest_rate=shema_op_props.hbd_interest_rate,
        account_subsidy_budget=shema_op_props.account_subsidy_budget,
        account_subsidy_decay=shema_op_props.account_subsidy_decay,
    )
)

# not yet set in WitnessSetProperties
assert wax_op.props.account_creation_fee is None
assert wax_op.props.hbd_exchange_rate is None

wax_op.props.account_creation_fee = (
    to_python_json_asset(shema_op_props.account_creation_fee)
    if shema_op_props.account_creation_fee is not None
    else None
)

# as_nai() gives Cannot create asset from {'amount': 100, 'nai': '@@000000013', 'precision': 3}.
# as_legacy() gives wax.exceptions.asset_errors.CannotCreateAssetError: Cannot create asset from 0.100 HBD.
# wax_op.props.hbd_exchange_rate = convert_to_python_price(shema_op_props.hbd_exchange_rate.base.as_legacy(), shema_op_props.hbd_exchange_rate.quote.as_legacy())
wax_op.props.hbd_exchange_rate = (
    python_price(
        base=to_python_json_asset(shema_op_props.hbd_exchange_rate.base),
        quote=to_python_json_asset(shema_op_props.hbd_exchange_rate.quote),
    )
    if shema_op_props.hbd_exchange_rate is not None
    else None
)

serialized_props = serialize_witness_set_properties(wax_op.props)
normalized_props = [(k.decode(), v.decode()) for k, v in serialized_props.items()]

schemas_op_actual = WitnessSetPropertiesOperation(owner="mee", props=normalized_props)
print(schemas_op_actual.json(indent=4))
