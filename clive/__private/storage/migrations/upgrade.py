# ruff: noqa: F401
from __future__ import annotations

from typing import TypeAlias

from clive.__private.storage.migrations import current, v1, v2
from clive.exceptions import CliveError


class CannotUpgradeStorageModelVersionError(CliveError):
    """Raise when trying to upgrade unknown storage model version to current version."""


class CannotParseStorageModelVersionError(CliveError):
    """Raise when trying to parse unknown storage model version."""


AllProfileStorageModels: TypeAlias = v1.ProfileStorageModel | v2.ProfileStorageModel


def upgrade_storage_model(model: AllProfileStorageModels) -> current.ProfileStorageModel:
    if isinstance(model, v1.ProfileStorageModel):
        model = v2.ProfileStorageModel(
            name=model.name,
            working_account=model.working_account,
            tracked_accounts=model.tracked_accounts,
            known_accounts=model.known_accounts,
            key_aliases=model.key_aliases,
            transaction=model.transaction,
            chain_id=model.chain_id,
            node_address=model.node_address,
        )
    if isinstance(model, current.ProfileStorageModel):
        return model
    raise CannotUpgradeStorageModelVersionError


def parse_and_upgrade_storage_model(content: str, version: str) -> current.ProfileStorageModel:
    model: AllProfileStorageModels
    match version:
        case "v1" | current.FIRST_VERSION:
            model = v1.ProfileStorageModel.parse_raw(content)
        case "v2":
            model = v2.ProfileStorageModel.parse_raw(content)
        case _:
            raise CannotParseStorageModelVersionError

    return upgrade_storage_model(model)
