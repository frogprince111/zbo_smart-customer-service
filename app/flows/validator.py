from app.core.errors import FlowError
from app.flows.models import Flow, FlowStepType


class FlowValidator:
    def validate(self, flow: Flow) -> None:
        if not flow.steps:
            raise FlowError(f"Flow {flow.id} 缺少 steps")
        for idx, step in enumerate(flow.steps):
            if step.type == FlowStepType.slot and not step.slot:
                raise FlowError(f"Flow {flow.id} 第 {idx} 步缺少 slot")
            if step.type == FlowStepType.action and not step.name:
                raise FlowError(f"Flow {flow.id} 第 {idx} 步缺少 action name")

    def validate_all(self, flows: dict[str, Flow]) -> None:
        for flow in flows.values():
            self.validate(flow)

