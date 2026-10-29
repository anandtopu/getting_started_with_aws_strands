"""Model-driven agents versus fixed workflows; tokens; ecosystem map (Python, TypeScript, tools,
Evals, builder, Bedrock, AgentCore, MCP, A2A).

Run: uv run python modules/00_setup/examples/01_agent_or_workflow.py --mock
Expected: Lesson complete.
Cost: mock/local $0 hosted inference; live hosted calls use tokens.
AWS required: No. Resources created: none.
"""

from strands import Agent

from common.lessons import complete, lesson_settings
from common.models import get_model
from common.pretty import console, run_cli


def main() -> None:
    _, cfg = lesson_settings()
    # A workflow always follows our branch; a model-driven agent chooses an answer.
    request = "Can Nimbus help me plan a trip?"
    workflow_answer = "Choose a destination." if "trip" in request else "Contact support."
    console.print("Workflow:", workflow_answer)
    # KEY IDEA: the Agent owns the model conversation; we give it a task.
    agent = Agent(
        model=get_model(cfg, responses=["Yes. Which destination and budget?"]),
        system_prompt="You are Nimbus. Ask for missing trip details.",
        callback_handler=None,
        retry_strategy=None,
    )
    complete(agent(request, limits={"turns": 2}), cfg)


if __name__ == "__main__":
    run_cli(main)
