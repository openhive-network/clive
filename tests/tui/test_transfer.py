import asyncio
from typing import Optional

import pytest
from _pytest.fixtures import FixtureRequest

from textual.pilot import Pilot

import test_tools as tt  # noqa: E402

from clive.__private.config import settings
from clive.__private.core.world import TextualWorld
from clive.__private.ui.app import Clive

# for debug purposes:
from clive.__private.ui.operations.cart_based_screen.cart_overview import CartItem

from .constants import *
from .utils import *
from .activate import activate

async def create_transfer(
    pilot: Pilot,
    beneficient: str,
    amount: str,
    asset_token: AssetToken,
    memo: str
) -> None:
    '''
        Assuming Transfer is current screen
    '''
    await write_text(pilot, beneficient)
    await press_keys(pilot, 'tab', 'tab')
    await write_text(pilot, amount)
    if asset_token == AssetToken.HBD:
        await press_keys(pilot, 'tab', 'tab')
    else: # HIVE
        await press_keys(pilot, 'tab', 'down', 'down', 'enter', 'tab')
    if memo:
        await write_text(pilot, memo)

testdata = [
    (True, AssetToken.HIVE, 'memo1', OperationProcessing.FAST_BROADCAST),
    (True, AssetToken.HIVE, None, OperationProcessing.FINALIZE_TRANSACTION),
    (True, AssetToken.HIVE, 'memo2', OperationProcessing.ADD_TO_CART),
    # (True, AssetToken.HBD, 'memo3', OperationProcessing.FAST_BROADCAST),
    # (True, AssetToken.HBD, None, OperationProcessing.FINALIZE_TRANSACTION),
    # (True, AssetToken.HBD, 'memo4', OperationProcessing.ADD_TO_CART),
    # (False, AssetToken.HIVE, 'memo1', OperationProcessing.FAST_BROADCAST),
    # (False, AssetToken.HIVE, None, OperationProcessing.FINALIZE_TRANSACTION),
    # (False, AssetToken.HIVE, 'memo2', OperationProcessing.ADD_TO_CART),
    # (False, AssetToken.HBD, 'memo3', OperationProcessing.FAST_BROADCAST),
    # (False, AssetToken.HBD, None, OperationProcessing.FINALIZE_TRANSACTION),
    # (False, AssetToken.HBD, 'memo4', OperationProcessing.ADD_TO_CART),
]

@pytest.mark.parametrize('activated, asset_token, memo, operation_processing', testdata)
async def test_transfer(
    prepared_env: tuple[tt.InitNode, Clive],
    request: FixtureRequest,
    activated: bool,
    asset_token: AssetToken,
    memo: Optional[str],
    operation_processing: OperationProcessing
) -> None:

    print(f"Enter '{request.node.name}' ...")
    USER = WORKING_ACCOUNT.name
    PASS = WORKING_ACCOUNT.name
    USER1 = WATCHED_ACCOUNTS[0].name
    AMOUNT = '1.03'

    node = prepared_env[0]
    app = prepared_env[1]

    async with app.run_test() as pilot:
        print("Enter 'async with app.run_test() as pilot' ...")
        current_view(app, True)
        assert get_mode(app) == 'inactive', "Expected 'inactive' mode!"

        if activated:
            await activate(pilot, PASS)
            assert get_mode(app) == 'active', "Expected 'active' mode!"

        # TODO: save balances before transfer
        ...

        ### Create transfer
        # Choose transfer operation
        await press_keys(pilot, 'f2', 'tab', 'enter')
        # Fill transfer data
        await create_transfer(pilot, USER1, AMOUNT, asset_token, memo)
        current_view(app, True)

        if operation_processing == OperationProcessing.ADD_TO_CART:
            await press_keys(pilot, 'f2', 'f2', 'f10', 'f10') # add to cart, go to cart, summary, finalize
        elif operation_processing == OperationProcessing.FAST_BROADCAST:
            await press_keys(pilot, 'f5')
        else: # FINALIZE_TRANSACTION
            await press_keys(pilot, 'f10', 'f10')

        current_view(app)

        if not activated:
            await activate(pilot, PASS)
            assert get_mode(app) == 'active', "Expected 'active' mode!"
        
        
        #cart_items = app.query(CartItem)
        #print(f'cart_items: {cart_items.nodes}')
        #for cart_item in cart_items.nodes:
        #    print(f'cart_item: {cart_item.renderable}')
        
        #await asyncio.sleep(3)
        node.wait_number_of_blocks(1)

        history = node.api.account_history.get_account_history(account=USER, include_reversible=True)['history']
        
        operation = history[-1][1]['op']
        print(f'operation: {operation}')
        assert operation['type'] == 'transfer_operation'
        expected = {
            'from': USER,
            'to': USER1,
            'amount': {
                'amount': str(int(float(AMOUNT) * 1000)),
                'precision': 3,
                'nai': '@@000000021'
            },
            'memo': memo if memo else ''
        }
        #print(f"operation['value']: {operation['value']}, expected: {expected}")
        assert operation['value'] == expected

        ### Quit
        await quit(pilot)
