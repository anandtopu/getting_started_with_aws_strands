"""Approve only matching nonempty reviewed digests. Run: uv run python
modules/bonus/B3_self_extending/solutions/01_digest.py. Cost $0; no resources."""


def solve(value):
    # YOUR CODE HERE: replace the baseline with the stated rule.
    return bool(value["reviewed"]) and value["current"] == value["reviewed"]


def main():
    print(solve({"current": "abc", "reviewed": "abc"}))


if __name__ == "__main__":
    main()
