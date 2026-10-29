"""Expose only the reviewed public quote fields; omit credentials and debug data.

Run: uv run python modules/18_a2a/solutions/02_public_offer.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return {k: value[k] for k in ("offer_id", "flight_id", "cents", "currency", "quote_only")}


def main() -> None:
    print(
        solve(
            {
                "offer_id": "u1",
                "flight_id": "f1",
                "cents": 7500,
                "currency": "USD",
                "quote_only": True,
                "token": "private",
            }
        )
    )


if __name__ == "__main__":
    main()
