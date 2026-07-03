from src.manager.pipeline import build_output, classify_ambiguity
from src.schema import ManagerInput, ManagerOutput, RoutingStrategy


class AlwaysClarify:
    name = "always_clarify"

    def predict(self, input_data: ManagerInput) -> ManagerOutput:
        return build_output(
            input_data,
            RoutingStrategy.CLARIFY,
            ambiguity=classify_ambiguity(input_data.command, input_data.scene_context),
        )
