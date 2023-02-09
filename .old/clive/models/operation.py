from __future__ import annotations

from dataclasses import dataclass

import yaml

from clive.abstract_class import AbstractClass


@dataclass
class Operation(AbstractClass):
    type_: str

    def as_yaml(self) -> str:
        return str(yaml.dump(self.__dict__))
