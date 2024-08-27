from __future__ import annotations

import errno
from dataclasses import dataclass
from pathlib import Path

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.constants.cli import PERFORM_WORKING_ACCOUNT_LOAD
from clive.__private.models.schemas import CustomJsonOperation
from clive.__private.validators.json_validator import JsonValidator


@dataclass(kw_only=True)
class ProcessCustomJson(OperationCommand):
    id_: str
    authorize_by_active: list[str]
    authorize: list[str]
    json_or_path: str

    async def _create_operation(self) -> CustomJsonOperation:
        json_ = self.ensure_json_from_json_string_or_path(self.json_or_path)
        return CustomJsonOperation(
            id_=self.id_,
            json_=json_,
            required_auths=self.authorize_by_active,
            required_posting_auths=self.authorize,
        )

    async def validate(self) -> None:
        self._validate_no_both_posting_and_active_auths()
        self._validate_at_least_one_active_or_posting_auth()
        await super().validate()

    def _validate_no_both_posting_and_active_auths(self) -> None:
        is_authorize_by_active_given = bool(self.authorize_by_active)
        is_authorize_given = bool(self.authorize) and not self.authorize_has_default_value
        if is_authorize_given and is_authorize_by_active_given:
            raise CLIPrettyError(
                "Transaction can't be signed by posting and active authority at the same time.", errno.EINVAL
            )

    def _validate_at_least_one_active_or_posting_auth(self) -> None:
        is_authorize_by_active_given = bool(self.authorize_by_active)
        is_authorize_given = bool(self.authorize)
        if not is_authorize_given and not is_authorize_by_active_given:
            raise CLIPrettyError(
                "At least one active or posting account authority is required. Can't use working account name"
                " as default. Perhaps you don't have a working account set?",
                errno.EINVAL,
            )

    async def _hook_before_entering_context_manager(self) -> None:
        #  posting authority default value shouldn't be used when active authority is requested
        if self.authorize_has_default_value and self.authorize_by_active:
            self.authorize = []
        await super()._hook_before_entering_context_manager()

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

    @property
    def authorize_has_default_value(self) -> bool:
        return len(self.authorize) == 1 and self.authorize[0] == PERFORM_WORKING_ACCOUNT_LOAD
