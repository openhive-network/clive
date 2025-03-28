# ruff: noqa: F401
from __future__ import annotations

from typing import TypeAlias

from clive.__private.models.schemas import Transaction
from clive.__private.storage.migrations import current, v1, v2
from clive.__private.storage.migrations.version import Version
from clive.exceptions import CliveError


class CannotUpgradeStorageModelVersionError(CliveError):
    """Raise when trying to upgrade unknown storage model version to current version."""


class CannotParseStorageModelVersionError(CliveError):
    """Raise when trying to parse unknown storage model version."""


AllProfileStorageModels: TypeAlias = v1.ProfileStorageModel | v2.ProfileStorageModel


def upgrade_storage_model(model: AllProfileStorageModels) -> current.ProfileStorageModel:
    if type(model) is v1.ProfileStorageModel:
        transaction = (
            v2.TransactionStorageModel(
                schemas_transaction=Transaction(
                    ref_block_num=model.transaction.transaction_core.ref_block_num,
                    ref_block_prefix=model.transaction.transaction_core.ref_block_prefix,
                    expiration=model.transaction.transaction_core.expiration,
                    extensions=model.transaction.transaction_core.extensions,
                    signatures=model.transaction.transaction_core.signatures,
                    operations=model.transaction.transaction_core.operations,
                ),
                transaction_file_path=model.transaction.transaction_file_path,
            )
            if model.transaction
            else None
        )
        model = v2.ProfileStorageModel(
            name=model.name,
            working_account=model.working_account,
            tracked_accounts=model.tracked_accounts,
            known_accounts=model.known_accounts,
            key_aliases=model.key_aliases,
            transaction=transaction,
            chain_id=model.chain_id,
            node_address=model.node_address,
        )
    if type(model) is current.ProfileStorageModel:
        return model
    raise CannotUpgradeStorageModelVersionError


def parse_and_upgrade_storage_model(content: str, version: Version) -> current.ProfileStorageModel:
    model: AllProfileStorageModels
    match version:
        case Version.V0 | Version.V1:
            model = v1.ProfileStorageModel.parse_raw(content)
        case Version.V2:
            model = v2.ProfileStorageModel.parse_raw(content)
        case _:
            raise CannotParseStorageModelVersionError

    return upgrade_storage_model(model)
