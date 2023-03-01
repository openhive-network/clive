from __future__ import annotations

import dataclasses
import json

from clive.abstract_class import AbstractClass


@dataclasses.dataclass
class Operation(AbstractClass):
    type_: str

    def as_json(self) -> str:
        return json.dumps(dataclasses.asdict(self), indent=4)
