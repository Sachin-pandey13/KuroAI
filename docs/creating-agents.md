# Creating Custom Agents

Agents in KuroAI process tasks and generate artifacts within the pipeline.

## Basic Structure

```python
from backend.contracts.task import Task
from backend.contracts.artifact import Artifact
from backend.engine.context_engine import ContextEngine

class CustomAgent:
    def __init__(self, name: str = "CustomAgent"):
        self.name = name

    def execute_task(self, task: Task, context_engine: ContextEngine) -> Artifact:
        context = context_engine.build_context(task.id)
        # Execute agent logic using context
        return Artifact(id="art_1", artifact_type="CUSTOM_OUTPUT", content="...")
```
