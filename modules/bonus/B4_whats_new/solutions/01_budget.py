"""Accept only positive bounded integer invocation budgets. Run: uv run python
modules/bonus/B4_whats_new/solutions/01_budget.py. Cost $0; no resources."""


def solve(value):
    # YOUR CODE HERE: replace the baseline with the stated rule.
    return type(value) is int and 1 <= value <= 3


def main():
    print(solve(3))


if __name__ == "__main__":
    main()
