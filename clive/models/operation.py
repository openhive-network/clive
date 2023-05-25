from __future__ import annotations

import json

from pydantic import BaseModel

from clive.__private.abstract_class import AbstractClass


class Operation(BaseModel, AbstractClass):
    def as_json(self, indent: int = 4) -> str:
        return json.dumps(self.dict(by_alias=True), indent=indent)
