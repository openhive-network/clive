from __future__ import annotations
from enum import Enum

from textual.app import App
from textual.pilot import Pilot


class AssetToken(Enum):
    HBD = 1
    HIVE = 2

class OperationProcessing(Enum):
    ADD_TO_CART = 1
    FAST_BROADCAST = 2
    FINALIZE_TRANSACTION = 3

async def press_keys(pilot: Pilot, *args: str) -> None:
    '''
        Emulate key presses from given sequence
    '''
    for arg in args:
        await pilot.press(arg)
        await pilot.pause()

async def write_text(pilot: Pilot, text: str) -> None:
    '''
        Useful for place text in any Input widget
    '''
    for c in text:
        await pilot.press(c)
    await pilot.pause()

def get_mode(app: App) -> str:
    '''
        Do not call while onboarding process
    '''
    return str(app.query_one("#mode-label").query_one("#value")._DynamicLabel__label.renderable).strip(' ')

async def quit(pilot: Pilot) -> None:
    '''
        Clean exit clive from any screen
    '''
    await press_keys(pilot, 'ctrl+x')
    current_view(pilot._app)
    await press_keys(pilot, 'ctrl+x')

def current_view(app: App, nodes: bool = False) -> None:
    '''
        For debug purposes
    '''
    print(f'screen: {app.screen}, focused: {app.focused}')
    if nodes:
        print(f'nodes: {app.query("*").nodes}')

