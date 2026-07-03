from typing import Protocol

from src.schema import ManagerInput, ManagerOutput


class System(Protocol):
    name: str

    def predict(self, input_data: ManagerInput) -> ManagerOutput:
        ...
