from src.manager.pipeline import build_output
from src.schema import ManagerInput, ManagerOutput, RoutingStrategy


class AlwaysResolve:
    name = "always_resolve"

    def predict(self, input_data: ManagerInput) -> ManagerOutput:
        return build_output(input_data, RoutingStrategy.SILENTLY_RESOLVE, slots={})
