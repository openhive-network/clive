from textual.pilot import Pilot

from .utils import *

async def activate_body(pilot: Pilot, password: str, view_info: bool = False) -> None:
    '''
        Do activate when Activate is current screen
    '''
    if view_info:
        current_view(app)
    await write_text(pilot, password)
    if view_info:
        current_view(app)
    await press_keys(pilot, 'f2')
    if view_info:
        current_view(app, True)

async def activate(pilot: Pilot, password: str, view_info: bool = False) -> None:
    '''
        Do activate when Dashboard is current screen
    '''
    await press_keys(pilot, 'f4')
    await activate_body(pilot, password, view_info)
