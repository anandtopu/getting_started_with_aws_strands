"""Runtime-hosted, JWT-bound policy and booking evidence with managed Memory and Gateway."""

from pydantic import BaseModel, ConfigDict, Field, SecretStr
from strands import tool

from common.agentcore_identity import cognito_identity, demo_identity
from common.agentcore_memory import preferences
from common.config import course_value
from common.coordination import worker
from common.gateway_booking import gateway_client
from common.models import get_guarded_model
from common.production_support import search_policies
from common.testing import tool_message


class CopilotRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: str = Field(pattern="^copilot$")
    access_token: SecretStr = Field(min_length=1, max_length=8192)
    prompt: str = Field(min_length=1, max_length=2000)


def hosted_copilot(payload, settings):
    request = CopilotRequest.model_validate(payload)
    mock = settings.provider == "mock"
    token = request.access_token.get_secret_value()
    identity = (
        demo_identity()
        if mock
        else cognito_identity(
            settings, token, course_value("NIMBUS_USER_POOL_ID"), course_value("NIMBUS_CLIENT_ID")
        )
    )
    memory_id = "NimbusDemo-1234567890" if mock else course_value("AGENTCORE_MEMORY_ID")
    if not memory_id:
        raise ValueError("Configure the Runtime Memory ID before enabling the copilot operation")
    used = []

    @tool
    def recall_preferences() -> dict:
        """Recall this verified actor's preferences; caller cannot choose another actor."""
        if used:
            raise ValueError("Preference recall already used")
        used.append(True)
        return preferences(settings, memory_id, identity["actor"])

    with gateway_client(
        settings, url=course_value("AGENTCORE_GATEWAY_URL"), token=token
    ) as gateway:
        tools = [t for t in gateway.list_tools_sync() if t.tool_name == "nimbus___search_flights"]
        if len(tools) != 1:
            raise ValueError("The reviewed public flight tool is unavailable")
        responses = [
            tool_message("search_policies", {"query": "refund supervisor"}),
            tool_message("recall_preferences", {}),
            tool_message("nimbus___search_flights", {"destination": "Porto"}),
            "[policies/refund.md] A $600 refund needs supervisor review. "
            "Porto flights are quotes only. Seat preference: aisle. No payment was made.",
        ]
        agent = worker(
            settings,
            "hosted_support_copilot",
            responses,
            model_calls=4,
            tools=[search_policies, recall_preferences, *tools],
            prompt="Retrieve policy evidence, recall preferences and search Porto alternatives. "
            "Cite policy sources. Quotes cannot authorize a booking or refund. "
            "The trusted host performs human approval; never claim a payment.",
        )
        agent.model = get_guarded_model(settings, responses=responses)
        result = agent(request.prompt, limits={"turns": 4})
        calls = [
            b["toolUse"]["name"] for m in agent.messages for b in m["content"] if "toolUse" in b
        ]
        required = {"search_policies", "recall_preferences", "nimbus___search_flights"}
        if result.stop_reason != "end_turn" or not required <= set(calls):
            raise ValueError("Hosted support did not obtain all required evidence")
        return {
            "answer": str(result),
            "tools": calls,
            "usage": dict(result.metrics.accumulated_usage),
            "approval_required": True,
            "payment_executed": False,
            "scope": "Runtime handler + local MCP + AWS contracts" if mock else "Live AWS",
        }
