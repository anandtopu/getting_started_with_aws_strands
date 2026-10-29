"""Accept a quote only when role, reference and integer cents match the catalog.

Run: uv run python modules/15_agents_as_tools/solutions/02_validate.py
Expected: sample output; check with module tests. Cost/resources: $0, none.
"""

from typing import Any


def solve(value: Any) -> Any:
    # Reference solution
    return all(
        type(value["answer"][k]) is type(value["catalog"][k])
        and value["answer"][k] == value["catalog"][k]
        for k in ("role", "reference", "cents")
    )


def main() -> None:
    print(
        solve(
            {
                "answer": {"role": "flight", "reference": "f1", "cents": 100},
                "catalog": {"role": "flight", "reference": "f1", "cents": 100},
            }
        )
    )


if __name__ == "__main__":
    main()
