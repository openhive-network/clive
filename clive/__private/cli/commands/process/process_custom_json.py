from __future__ import annotations

import contextlib
import errno
import json
from dataclasses import dataclass
from pathlib import Path

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
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
        self._validate_no_posting_and_active_auths()
        await super().validate()

    def _validate_no_posting_and_active_auths(self) -> None:
        active_auths_number = len(self.required_auths)
        posting_auths_number = len(self.required_posting_auths)
        if active_auths_number != 0 and posting_auths_number != 0:
            raise CLIPrettyError(
                "Transaction can't be signed by posting and active authority at the same time.", errno.EINVAL
            )

    @staticmethod
    def ensure_json_from_json_string_or_path(json_or_path: str) -> str:
        # Try to parse the string as JSON
        with contextlib.suppress(json.JSONDecodeError):
            json.loads(json_or_path)
            return json_or_path
        # Otherwise ensure that the input is a valid file path
        json_path = Path(json_or_path)
        if not json_path.is_file():
            raise CLIPrettyError("The input is neither a valid JSON string nor a valid file path.", errno.EINVAL)

        # Read the file contents
        with json_path.open() as file:
            try:
                json_string = file.read()
                json.loads(json_string)
                return json_string  # noqa: TRY300
            except json.JSONDecodeError as err:
                raise CLIPrettyError(f"The {json_path} file does not contain a valid JSON.", errno.EINVAL) from err
