"""Keep generation within the reviewed quote inventory. Run: uv run python
modules/bonus/B3_self_extending/solutions/02_inventory.py. Cost $0; no resources."""


def solve(value):
    # YOUR CODE HERE: replace the baseline with the stated rule.
    return value in {"baggage_fee", "seat_quote"}


def main():
    print(solve("baggage_fee"))


if __name__ == "__main__":
    main()
