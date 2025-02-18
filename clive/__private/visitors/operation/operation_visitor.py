from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.__private.models import schemas


class OperationVisitor:
    def visit(self, operation: schemas.OperationUnion) -> None:
        """Determine the correct method to call based on operation type."""
        operation_name = operation.get_name_with_suffix()
        method_name = f"visit_{operation_name}"
        visit_method = getattr(self, method_name, None)
        assert visit_method is not None, f"No visit method defined for {operation_name}"
        visit_method(operation)

    def visit_account_create_operation(self, operation: schemas.AccountCreateOperation) -> None:
        self._default_visit(operation)

    def visit_account_create_with_delegation_operation(
        self, operation: schemas.AccountCreateWithDelegationOperation
    ) -> None:
        self._default_visit(operation)

    def visit_account_update2_operation(self, operation: schemas.AccountUpdate2Operation) -> None:
        self._default_visit(operation)

    def visit_account_update_operation(self, operation: schemas.AccountUpdateOperation) -> None:
        self._default_visit(operation)

    def visit_account_witness_proxy_operation(self, operation: schemas.AccountWitnessProxyOperation) -> None:
        self._default_visit(operation)

    def visit_account_witness_vote_operation(self, operation: schemas.AccountWitnessVoteOperation) -> None:
        self._default_visit(operation)

    def visit_cancel_transfer_from_savings_operation(
        self, operation: schemas.CancelTransferFromSavingsOperation
    ) -> None:
        self._default_visit(operation)

    def visit_change_recovery_account_operation(self, operation: schemas.ChangeRecoveryAccountOperation) -> None:
        self._default_visit(operation)

    def visit_claim_account_operation(self, operation: schemas.ClaimAccountOperation) -> None:
        self._default_visit(operation)

    def visit_claim_reward_balance_operation(self, operation: schemas.ClaimRewardBalanceOperation) -> None:
        self._default_visit(operation)

    def visit_collateralized_convert_operation(self, operation: schemas.CollateralizedConvertOperation) -> None:
        self._default_visit(operation)

    def visit_comment_operation(self, operation: schemas.CommentOperation) -> None:
        self._default_visit(operation)

    def visit_comment_options_operation(self, operation: schemas.CommentOptionsOperation) -> None:
        self._default_visit(operation)

    def visit_convert_operation(self, operation: schemas.ConvertOperation) -> None:
        self._default_visit(operation)

    def visit_create_claimed_account_operation(self, operation: schemas.CreateClaimedAccountOperation) -> None:
        self._default_visit(operation)

    def visit_create_proposal_operation(self, operation: schemas.CreateProposalOperation) -> None:
        self._default_visit(operation)

    def visit_custom_binary_operation(self, operation: schemas.CustomBinaryOperation) -> None:
        self._default_visit(operation)

    def visit_custom_json_operation(self, operation: schemas.CustomJsonOperation) -> None:
        self._default_visit(operation)

    def visit_custom_operation(self, operation: schemas.CustomOperation) -> None:
        self._default_visit(operation)

    def visit_decline_voting_rights_operation(self, operation: schemas.DeclineVotingRightsOperation) -> None:
        self._default_visit(operation)

    def visit_delegate_vesting_shares_operation(self, operation: schemas.DelegateVestingSharesOperation) -> None:
        self._default_visit(operation)

    def visit_delete_comment_operation(self, operation: schemas.DeleteCommentOperation) -> None:
        self._default_visit(operation)

    def visit_escrow_approve_operation(self, operation: schemas.EscrowApproveOperation) -> None:
        self._default_visit(operation)

    def visit_escrow_dispute_operation(self, operation: schemas.EscrowDisputeOperation) -> None:
        self._default_visit(operation)

    def visit_escrow_release_operation(self, operation: schemas.EscrowReleaseOperation) -> None:
        self._default_visit(operation)

    def visit_escrow_transfer_operation(self, operation: schemas.EscrowTransferOperation) -> None:
        self._default_visit(operation)

    def visit_feed_publish_operation(self, operation: schemas.FeedPublishOperation) -> None:
        self._default_visit(operation)

    def visit_limit_order_cancel_operation(self, operation: schemas.LimitOrderCancelOperation) -> None:
        self._default_visit(operation)

    def visit_limit_order_create_2_operation(self, operation: schemas.LimitOrderCreate2Operation) -> None:
        self._default_visit(operation)

    def visit_limit_order_create_operation(self, operation: schemas.LimitOrderCreateOperation) -> None:
        self._default_visit(operation)

    def visit_pow_operation(self, operation: schemas.PowOperation) -> None:
        self._default_visit(operation)

    def visit_pow_2_operation(self, operation: schemas.Pow2Operation) -> None:
        self._default_visit(operation)

    def visit_recover_account_operation(self, operation: schemas.RecoverAccountOperation) -> None:
        self._default_visit(operation)

    def visit_recurrent_transfer_operation(self, operation: schemas.RecurrentTransferOperation) -> None:
        self._default_visit(operation)

    def visit_remove_proposal_operation(self, operation: schemas.RemoveProposalOperation) -> None:
        self._default_visit(operation)

    def visit_request_account_recovery_operation(self, operation: schemas.RequestAccountRecoveryOperation) -> None:
        self._default_visit(operation)

    def visit_reset_account_operation(self, operation: schemas.ResetAccountOperation) -> None:
        self._default_visit(operation)

    def visit_set_reset_account_operation(self, operation: schemas.SetResetAccountOperation) -> None:
        self._default_visit(operation)

    def visit_set_withdraw_vesting_route_operation(self, operation: schemas.SetWithdrawVestingRouteOperation) -> None:
        self._default_visit(operation)

    def visit_transfer_from_savings_operation(self, operation: schemas.TransferFromSavingsOperation) -> None:
        self._default_visit(operation)

    def visit_transfer_operation(self, operation: schemas.TransferOperation) -> None:
        self._default_visit(operation)

    def visit_transfer_to_savings_operation(self, operation: schemas.TransferToSavingsOperation) -> None:
        self._default_visit(operation)

    def visit_transfer_to_vesting_operation(self, operation: schemas.TransferToVestingOperation) -> None:
        self._default_visit(operation)

    def visit_update_proposal_operation(self, operation: schemas.UpdateProposalOperation) -> None:
        self._default_visit(operation)

    def visit_update_proposal_votes_operation(self, operation: schemas.UpdateProposalVotesOperation) -> None:
        self._default_visit(operation)

    def visit_vote_operation(self, operation: schemas.VoteOperation) -> None:
        self._default_visit(operation)

    def visit_withdraw_vesting_operation(self, operation: schemas.WithdrawVestingOperation) -> None:
        self._default_visit(operation)

    def visit_witness_block_approve_operation(self, operation: schemas.WitnessBlockApproveOperation) -> None:
        self._default_visit(operation)

    def visit_witness_set_properties_operation(self, operation: schemas.WitnessSetPropertiesOperation) -> None:
        self._default_visit(operation)

    def visit_witness_update_operation(self, operation: schemas.WitnessUpdateOperation) -> None:
        self._default_visit(operation)

    def _default_visit(self, operation: schemas.OperationUnion) -> None:
        """Fallback if no specific method exists for an operation type."""
