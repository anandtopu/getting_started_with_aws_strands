"""Reload only after review and a passing contract. Run: uv run python
modules/bonus/B3_self_extending/solutions/03_reload.py. Cost $0; no resources."""


def solve(value):
    # YOUR CODE HERE: replace the baseline with the stated rule.
    return value["reviewed"] is True and value["tested"] is True


def main():
    print(solve({"reviewed": True, "tested": True}))


if __name__ == "__main__":
    main()
