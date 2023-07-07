from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(kw_only=True)
class ExternalCLICommand(ABC):
    @abstractmethod
    def run(self) -> None:
        """Run the command."""
