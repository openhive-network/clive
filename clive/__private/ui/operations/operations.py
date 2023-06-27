from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.widgets import Button, Static

from clive.__private.ui.operations.cart import Cart
from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.operations_with_buttons_list import OPERATIONS_AND_BUTTONS
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.models import Operation


class Operations(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f2", "cart", "Cart"),
    ]

    def create_left_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Select one of the following operations:", id="hint")
            yield CliveButton("Transfer to account", id_="account-transfer-button")
            yield CliveButton("Transfer to savings", id_="savings-transfer-button")
            yield CliveButton("Transfer to vesting", id_="vesting-transfer-button")
            yield CliveButton("Vote", id_="vote-button")
            yield CliveButton("Convert", id_="convert-button")
            yield CliveButton("Account witness vote", id_="account-witness-vote-button")
            yield CliveButton("Witness block approve", id_="witness-block-approve-button")
            yield CliveButton("Account witness proxy", id_="account-witness-proxy-button")
            yield CliveButton("Cancel transfer from savings", id_="cancel-transfer-from-savings-button")
            yield CliveButton("Change recovery account", id_="change-recovery-account-button")
            yield CliveButton("Claim account", id_="claim-account-button")
            yield CliveButton("Withdraw vesting", id_="withdraw-vesting-button")
            yield CliveButton("Update proposal votes", id_="update-proposal-votes-button")
            yield CliveButton("Update proposal", id_="update-proposal-button")
            yield CliveButton("Transfer from savings", id_="transfer-from-savings-button")
            yield CliveButton("Set withdraw vesting route", id_="set-withdraw-vesting-route-button")
            yield CliveButton("Set reset account", id_="set-reset-account-button")
            yield CliveButton("Remove proposal", id_="remove-proposal-button")
            yield CliveButton("Recurrent transfer", id_="recurrent-transfer-button")
            yield CliveButton("Limit order create", id_="limit-order-create-button")
            yield CliveButton("Limit order cancel", id_="limit-order-cancel-button")
            yield CliveButton("Escrow transfer", id_="escrow-transfer-button")
            yield CliveButton("Escrow release", id_="escrow-release-button")
            yield CliveButton("Escrow dispute", id_="escrow-dispute-button")
            yield CliveButton("Escrow approve", id_="escrow-approve-button")
            yield CliveButton("Delete comment", id_="delete-comment-button")
            yield CliveButton("Delegate vesting shares", id_="delegate-vesting-shares-button")
            yield CliveButton("Decline voting rights", id_="decline-voting-rights-button")
            yield CliveButton("Custom", id_="custom-button")
            yield CliveButton("Custom json", id_="custom-json-button")
            yield CliveButton("Create proposal", id_="create-proposal-button")
            yield CliveButton("Comment options", id_="comment-options-button")
            yield CliveButton("Comment", id_="comment-button")
            yield CliveButton("Claim reward balance", id_="claim-reward-balance-button")
            yield CliveButton("Power up", id_="power-up-button")
            yield CliveButton("Power down", id_="power-down-button")

    def create_operation(self) -> Operation | None:
        """Not implemented here"""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id in OPERATIONS_AND_BUTTONS:
            button_id = event.button.id
            self.app.push_screen(OPERATIONS_AND_BUTTONS[button_id]())
        else:
            Notification("Not implemented yet!", category="error").show()

    def action_cart(self) -> None:
        if not self.app.world.profile_data.cart:
            Notification("There are no operations in the cart! Cannot continue.", category="warning").show()
            return

        self.app.push_screen(Cart())
