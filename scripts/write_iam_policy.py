"""Write a local inference-only IAM document from explicitly supplied ARNs.

Run: uv run python scripts/write_iam_policy.py --help
No AWS calls or resources. The administrator reviews and attaches the output.
"""

import argparse
import json
from pathlib import Path


def inference_policy(profile_arn: str, model_arns: list[str]) -> dict:
    resources = [profile_arn, *model_arns]
    if not model_arns or any(
        "*" in arn or "?" in arn or not arn.startswith("arn:aws") for arn in resources
    ):
        raise ValueError("Supply explicit profile and foundation-model ARNs without wildcards.")
    if ":inference-profile/" not in profile_arn:
        raise ValueError("The profile ARN must identify an inference-profile.")
    if any(":foundation-model/" not in arn for arn in model_arns):
        raise ValueError("Every destination must identify a foundation-model.")
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "InvokeOnlyConfiguredCourseModel",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",  # Converse authorization for the chosen model/profile.
                    "bedrock:InvokeModelWithResponseStream",  # ConverseStream for streamed answers.
                ],
                "Resource": resources,
            }
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-arn", required=True)
    parser.add_argument("--model-arns", nargs="+", required=True)
    parser.add_argument("--output", type=Path, default=Path(".nimbus/iam/bedrock-invoke.json"))
    args = parser.parse_args()
    document = inference_policy(args.profile_arn, args.model_arns)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(document, indent=2) + "\n")
    print(f"Wrote {args.output}. No AWS API called; review before attaching.")


if __name__ == "__main__":
    main()
