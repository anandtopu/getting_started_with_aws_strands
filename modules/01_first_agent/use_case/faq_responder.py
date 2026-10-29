"""Answer Nimbus FAQs from one policy and abstain when evidence is missing.

Run: uv run python modules/01_first_agent/use_case/faq_responder.py --mock
Expected: a Nimbus result followed by Lesson complete.
Cost: mock/local $0 hosted inference; hosted mode uses model tokens.
AWS resources created: none. Concepts: compose this module's taught APIs.
"""

from common.assistant import faq_agent
from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli


def main() -> None:
    _, cfg = lesson_settings()
    replies = [
        "A full refund needs cancellation within 24 hours and departure at least 7 days "
        "after creation (POL-REF-001).",
        "I do not know; the supplied policy does not cover visas.",
    ]
    agent = faq_agent(cfg, replies)
    # KEY IDEA: supplying a policy constrains the task, but grounding must still be evaluated.
    for question in ["When can I receive a full refund?", "Which visa do I need?"]:
        console.print("Traveler:", question)
        complete(agent(question, limits={"turns": 2}), cfg)


if __name__ == "__main__":
    run_cli(main)
