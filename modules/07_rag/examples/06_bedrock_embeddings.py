"""AWS optional: Titan embeddings use InvokeModel because Converse does not embed.

Run: uv run python modules/07_rag/examples/06_bedrock_embeddings.py --mock
Expected: Lesson complete.
Cost: offline $0; live model/embedding calls use configured rates.
AWS resources created by this script: none. Optional labs have separate CDK/cleanup.
"""

from common.aws_retrieval import titan_vector
from common.lessons import complete, lesson_settings
from common.pretty import console, run_cli
from common.retrieval import cosine


def main() -> None:
    args, cfg = lesson_settings()
    # KEY IDEA: embedding inference has a different API from chat inference.
    vector = titan_vector("Nimbus refund policy", mock=args.mock)
    console.print("Dimensions:", len(vector), "self cosine:", cosine(vector, vector))
    complete()


if __name__ == "__main__":
    run_cli(main)
