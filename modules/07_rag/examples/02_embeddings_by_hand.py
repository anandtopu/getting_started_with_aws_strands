"""Compute cosine similarity and plot a deliberately limited 2D teaching projection.

Run: uv run --group rag python modules/07_rag/examples/02_embeddings_by_hand.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

import matplotlib

from common.config import ROOT
from common.retrieval import cosine

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli


def main() -> None:
    args, cfg = lesson_settings()
    vectors = {"refund timing": [3, 1], "refund approval": [2, 1], "aisle seat": [0, 3]}
    console.print("Dot=7; norms=sqrt(10),sqrt(5); cosine:", cosine([3, 1], [2, 1]))
    # KEY IDEA: directions can be similar even when vector lengths differ.
    fig, ax = plt.subplots(figsize=(7, 4))
    for label, (x, y) in vectors.items():
        ax.scatter(x, y, s=60)
        ax.annotate(label, (x, y), xytext=(8, 8), textcoords="offset points")
    ax.set(
        xlim=(-0.3, 4.1),
        ylim=(0, 3.7),
        xlabel="Illustrative refund dimension",
        ylabel="Illustrative preference dimension",
        title="Toy vectors, not learned model embeddings",
    )
    ax.grid(alpha=0.2)
    fig.tight_layout()
    output = ROOT / ".nimbus/embedding_geometry.png"
    output.parent.mkdir(exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)
    console.print("Plot:", str(output))
    complete()


if __name__ == "__main__":
    run_cli(main)
