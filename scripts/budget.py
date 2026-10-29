"""Plan, create or delete one tagged $10 monthly budget. Default: local plan only.

Run: uv run python scripts/budget.py --email learner@example.com
Expected: budget plan, no AWS call. --create/--delete need explicit user invocation.
Resource: one monthly budget. Monitoring/email cost: $0/month; no Budget Actions.
Teardown: uv run python scripts/budget.py --delete
"""

import argparse
import json
from typing import Any

import boto3

from common.config import CourseError, load_settings
from common.pretty import run_cli

BUDGET_NAME = "nimbus-course-monthly"


def budget_request(account_id: str, email: str) -> dict[str, Any]:
    if "@" not in email or any(c.isspace() for c in email):
        raise CourseError("Provide one valid notification email address.")
    return {
        "AccountId": account_id,
        "Budget": {
            "BudgetName": BUDGET_NAME,
            "BudgetLimit": {"Amount": "10", "Unit": "USD"},
            "TimeUnit": "MONTHLY",
            "BudgetType": "COST",
        },
        "NotificationsWithSubscribers": [
            {
                "Notification": {
                    "NotificationType": "ACTUAL",
                    "ComparisonOperator": "GREATER_THAN",
                    "Threshold": threshold,
                    "ThresholdType": "PERCENTAGE",
                },
                "Subscribers": [{"SubscriptionType": "EMAIL", "Address": email}],
            }
            for threshold in (50, 80, 100)
        ],
        "ResourceTags": [{"Key": "project", "Value": "getting-started-with-aws-strands"}],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--create", action="store_true")
    actions.add_argument("--delete", action="store_true")
    parser.add_argument("--email", default="learner@example.com")
    args = parser.parse_args()
    if not (args.create or args.delete):
        print(json.dumps(budget_request("ACCOUNT_FROM_SSO_ON_CREATE", args.email), indent=2))
        print("Local plan only. No AWS API called.")
        return
    if args.create and args.email.endswith(("@example.com", "@example.org", "@example.net")):
        raise CourseError("Replace the example notification address with your own email.")
    cfg = load_settings()
    session = boto3.Session(profile_name=cfg.aws_profile or None, region_name=cfg.aws_region)
    identity = session.client("sts").get_caller_identity()
    if identity["Arn"].endswith(":root"):
        raise CourseError("Use an SSO identity, never root.")
    client = session.client("budgets")
    if args.delete:
        client.delete_budget(AccountId=identity["Account"], BudgetName=BUDGET_NAME)
        print("Budget deleted. Confirm it no longer appears in AWS Budgets.")
    else:
        client.create_budget(**budget_request(identity["Account"], args.email))
        print("Budget created. Verify notifications in AWS Budgets; alerts are not spending caps.")


if __name__ == "__main__":
    run_cli(main)
