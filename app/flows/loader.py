from pathlib import Path

import yaml

from app.flows.models import Flow


class FlowLoader:
    """从 YAML 加载 Flow 定义。"""

    def __init__(self, flow_dir: str | Path):
        self.flow_dir = Path(flow_dir)

    def load_all(self) -> dict[str, Flow]:
        flows: dict[str, Flow] = {}
        for path in sorted(self.flow_dir.glob("*.yaml")):
            flow = Flow.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
            flows[flow.id] = flow
        return flows

