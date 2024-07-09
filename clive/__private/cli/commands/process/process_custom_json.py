from __future__ import annotations

import errno
from dataclasses import dataclass
from pathlib import Path

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.validators.json_validator import JsonValidator
from clive.models.aliased import CustomJsonOperation


@dataclass(kw_only=True)
class ProcessCustomJson(OperationCommand):
    id_: str
    required_auths: list[str]
    required_posting_auths: list[str]
    json_or_path: str

    async def _create_operation(self) -> CustomJsonOperation:
        json_ = self.ensure_json_from_json_string_or_path(self.json_or_path)
        return CustomJsonOperation(
            id_=self.id_,
            json_=json_,
            required_auths=self.required_auths,
            required_posting_auths=self.required_posting_auths,
        )

    async def validate(self) -> None:
        self._validate_no_both_posting_and_active_auths()
        self._validate_at_least_one_active_or_posting_auth()
        await super().validate()

    def _validate_no_both_posting_and_active_auths(self) -> None:
        is_required_auths_given = bool(self.required_auths)
        is_required_posting_auths_given = bool(self.required_posting_auths)
        if is_required_auths_given and is_required_posting_auths_given:
            raise CLIPrettyError(
                "Transaction can't be signed by posting and active authority at the same time.", errno.EINVAL
            )

    def _validate_at_least_one_active_or_posting_auth(self) -> None:
        is_required_auths_given = bool(self.required_auths)
        is_required_posting_auths_given = bool(self.required_posting_auths)
        if not is_required_auths_given and not is_required_posting_auths_given:
            raise CLIPrettyError(
                "At least one active or posting account authority is required. Can't use working account name"
                " as default. Perhaps you don't have a working account set?",
                errno.EINVAL,
            )

    @staticmethod
    def ensure_json_from_json_string_or_path(json_or_path: str) -> str:
        validator = JsonValidator()

        # Try to parse the string as JSON
        result_from_string = validator.validate(json_or_path)
        if result_from_string.is_valid:
            return json_or_path

        # Otherwise ensure that the input is a valid file path
        json_path = Path(json_or_path)
        if not json_path.is_file():
            raise CLIPrettyError("The input is neither a valid JSON string nor a valid file path.", errno.EINVAL)

        # Read the file contents
        with json_path.open() as file:
            json_string = file.read()

            result_from_file = validator.validate(json_string)
            if not result_from_file.is_valid:
                raise CLIPrettyError(f"The {json_path} file does not contain a valid JSON.", errno.EINVAL)

            return json_string
