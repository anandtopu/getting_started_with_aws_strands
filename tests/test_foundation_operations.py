"""Exercise offline isolation and real botocore/moto contracts without AWS."""

import socket
from datetime import UTC, datetime

import boto3
import pytest
from botocore.stub import Stubber
from moto import mock_aws

from scripts.budget import budget_request
from scripts.find_leftovers import TAG_KEY, TAG_VALUE, scan_region
from scripts.write_iam_policy import inference_policy


def client(service):
    return boto3.client(
        service,
        region_name="us-east-1",
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
    )


def test_external_dns_tcp_and_udp_fail_before_connecting():
    with pytest.raises(OSError, match="External network disabled"):
        socket.getaddrinfo("example.com", 443)
    for lookup in (socket.gethostbyname, socket.gethostbyname_ex, socket.gethostbyaddr):
        with pytest.raises(OSError, match="External network disabled"):
            lookup("192.0.2.1")
    with socket.socket() as connection:
        with pytest.raises(OSError, match="External network disabled"):
            connection.connect(("192.0.2.1", 443))
        with pytest.raises(OSError, match="External network disabled"):
            connection.connect_ex(("192.0.2.1", 443))
    with socket.socket(type=socket.SOCK_DGRAM) as connection:
        with pytest.raises(OSError, match="External network disabled"):
            connection.sendto(b"test", ("192.0.2.1", 53))


def test_loopback_socketpair_supports_async_runtime():
    left, right = socket.socketpair()
    with left, right:
        left.settimeout(2)
        right.settimeout(2)
        left.sendall(b"local")
        assert right.recv(5) == b"local"


def test_budget_request_matches_installed_aws_contract():
    budgets = client("budgets")
    request = budget_request("123456789012", "learner@example.com")
    with Stubber(budgets) as stub:
        stub.add_response("create_budget", {}, request)
        assert budgets.create_budget(**request) == {}
    assert request["Budget"]["BudgetLimit"]["Amount"] == "10"
    assert [n["Notification"]["Threshold"] for n in request["NotificationsWithSubscribers"]] == [
        50,
        80,
        100,
    ]


def test_inventory_pagination_and_untagged_stack_child():
    tags, cfn = client("resourcegroupstaggingapi"), client("cloudformation")
    stack = "arn:aws:cloudformation:us-east-1:123456789012:stack/nimbus/test"
    now = datetime(2026, 10, 29, tzinfo=UTC)
    with Stubber(tags) as tag_stub, Stubber(cfn) as cfn_stub:
        filters = [{"Key": TAG_KEY, "Values": [TAG_VALUE]}]
        tag_stub.add_response(
            "get_resources",
            {
                "PaginationToken": "next",
                "ResourceTagMappingList": [],
            },
            {"TagFilters": filters},
        )
        tag_stub.add_response(
            "get_resources",
            {
                "ResourceTagMappingList": [{"ResourceARN": "arn:aws:s3:::nimbus-fixture"}],
            },
            {"TagFilters": filters, "PaginationToken": "next"},
        )
        cfn_stub.add_response(
            "describe_stacks",
            {
                "Stacks": [
                    {
                        "StackId": stack,
                        "StackName": "nimbus",
                        "CreationTime": now,
                        "StackStatus": "CREATE_COMPLETE",
                        "Tags": [{"Key": TAG_KEY, "Value": TAG_VALUE}],
                    }
                ]
            },
            {},
        )
        cfn_stub.add_response(
            "list_stack_resources",
            {
                "StackResourceSummaries": [
                    {
                        "LogicalResourceId": "Child",
                        "PhysicalResourceId": "untagged-child",
                        "ResourceType": "AWS::Logs::LogGroup",
                        "LastUpdatedTimestamp": now,
                        "ResourceStatus": "CREATE_COMPLETE",
                    }
                ]
            },
            {"StackName": stack},
        )
        report = scan_region(tags, cfn, "us-east-1")
        assert not report["errors"]
        assert {r["id"] for r in report["resources"]} == {
            stack,
            "untagged-child",
            "arn:aws:s3:::nimbus-fixture",
        }
        tag_stub.assert_no_pending_responses()
        cfn_stub.assert_no_pending_responses()


def test_inventory_denied_is_not_a_clean_scan():
    tags, cfn = client("resourcegroupstaggingapi"), client("cloudformation")
    with Stubber(tags) as tag_stub, Stubber(cfn) as cfn_stub:
        tag_stub.add_client_error("get_resources", "AccessDeniedException")
        cfn_stub.add_response("describe_stacks", {"Stacks": []})
        report = scan_region(tags, cfn, "us-east-1")
        assert report["resources"] == [] and report["errors"][0]["service"] == "tagging"


def test_explicit_inference_resources_and_wildcard_rejection():
    profile = "arn:aws:bedrock:us-east-1:123456789012:inference-profile/us.course"
    model = "arn:aws:bedrock:us-east-1::foundation-model/course"
    statement = inference_policy(profile, [model])["Statement"][0]
    assert statement["Resource"] == [profile, model]
    assert len(statement["Action"]) == 2
    with pytest.raises(ValueError, match="without wildcards"):
        inference_policy(profile, [model + "*"])


@mock_aws
def test_s3_fixture_round_trip_and_cleanup():
    """Validate moto isolation before later S3 session exercises depend on it."""
    s3 = client("s3")
    s3.create_bucket(Bucket="nimbus-offline-fixture")
    s3.put_object(Bucket="nimbus-offline-fixture", Key="session.json", Body=b'{"turns": 1}')
    response = s3.get_object(Bucket="nimbus-offline-fixture", Key="session.json")
    assert response["Body"].read() == b'{"turns": 1}'
    s3.delete_object(Bucket="nimbus-offline-fixture", Key="session.json")
    s3.delete_bucket(Bucket="nimbus-offline-fixture")
    assert s3.list_buckets()["Buckets"] == []
