"""Discard queued audio after an interruption. Run: uv run python
modules/bonus/B1_voice/solutions/01_playback.py. Cost $0; no resources."""


def solve(value):
    # YOUR CODE HERE: replace the baseline with the stated rule.
    return [] if value["barge_in"] else value["chunks"]


def main():
    print(solve({"barge_in": True, "chunks": [1, 2]}))


if __name__ == "__main__":
    main()
