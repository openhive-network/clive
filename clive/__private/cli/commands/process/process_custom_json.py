from __future__ import annotations

import errno
import json
from dataclasses import dataclass, field
from pathlib import Path

from clive.__private.cli.commands.abc.perform_actions_on_transaction_command import PerformActionsOnTransactionCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.validators.path_validator import PathValidator
from schemas.operations import CustomJsonOperation


@dataclass(kw_only=True)
class ProcessCustomJson(PerformActionsOnTransactionCommand):
    _operations: list[CustomJsonOperation] = field(default_factory=list)
    id_: str
    required_auths: list[str]
    required_posting_auths: list[str]

    def add_custom_json(self, *, json_or_path: str) -> None:
        json_: str = json_or_path if not self._is_valid_file_path(json_or_path) else self._load_from_file(json_or_path)
        self._validate_json(json_)
        self._operations.append(
            CustomJsonOperation(
                id_=self.id_,
                json_=json_,
                required_auths=self.required_auths,
                required_posting_auths=self.required_posting_auths,
            )
        )

    def add_follow_operation(self, *, follower: str, following: str, what: list[str]) -> None:
        raise NotImplementedError

    async def _get_transaction_content(self) -> list[CustomJsonOperation]:
        return self._operations

    def _is_valid_file_path(self, checked_path: str) -> bool:
        result = PathValidator(mode="is_file").validate(checked_path)
        return result.is_valid

    def _load_from_file(self, path: str) -> str:
        with Path(path).open("r", encoding="utf-8") as file:
            return file.read()

    async def validate(self) -> None:
        """Validate before creating whole transaction."""
        self._validate_no_posting_and_active_auths()

        await super().validate()

    def _validate_no_posting_and_active_auths(self) -> None:
        active_auths_number = sum([len(operation.required_auths) for operation in self._operations])
        posting_auths_number = sum([len(operation.required_posting_auths) for operation in self._operations])
        if active_auths_number != 0 and posting_auths_number != 0:
            raise CLIPrettyError(
                "Transaction can't be signed by posting and active authority at the same time.", errno.EINVAL
            )

    def _validate_json(self, json_: str) -> None:
        """Validate before creating operation."""
        try:
            json.loads(json_)
        except json.JSONDecodeError as err:
            raise CLIPrettyError(f"Invalid json format\n`{json_}`\n{err}", errno.EINVAL) from err
