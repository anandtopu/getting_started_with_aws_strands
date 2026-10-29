"""Input-only scripted predictions for replay; not a measure of language-model quality."""

from common.schemas import TicketTriage


def fixture_triage(text: str) -> dict:
    lowered = text.lower()
    category = next(
        (
            name
            for word, name in [
                ("refund", "refund"),
                ("change", "change"),
                ("bag", "baggage"),
                ("delete", "privacy"),
            ]
            if word in lowered
        ),
        "booking",
    )
    return TicketTriage(
        category=category,
        urgency="high" if "18 hours" in lowered else "normal",
        summary="Synthetic Nimbus support request.",
    ).model_dump(mode="json")
