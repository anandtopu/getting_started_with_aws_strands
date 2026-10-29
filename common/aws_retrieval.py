"""Verified Bedrock retrieval, embedding and rerank request shapes; no resource creation."""

import io
import json
from contextlib import contextmanager

import boto3
from botocore.config import Config
from botocore.response import StreamingBody
from botocore.stub import Stubber

from common.config import course_value, load_settings


def aws_client(service: str, *, mock: bool):
    cfg = load_settings(provider="bedrock")
    session = boto3.Session(
        region_name=cfg.aws_region,
        **(
            {"aws_access_key_id": "testing", "aws_secret_access_key": "testing"}
            if mock
            else {"profile_name": cfg.aws_profile or None}
        ),
    )
    return session.client(
        service, config=Config(connect_timeout=5, read_timeout=30, retries={"max_attempts": 1})
    )


@contextmanager
def knowledge_store(mock: bool):
    from strands.vended_memory_stores.bedrock_knowledge_base import BedrockKnowledgeBaseStore

    client = aws_client("bedrock-agent-runtime", mock=mock)
    kb = "KBDEMO1234" if mock else course_value("NIMBUS_KNOWLEDGE_BASE_ID")
    if not kb:
        raise ValueError("Set NIMBUS_KNOWLEDGE_BASE_ID after deploying the optional lab")
    store = BedrockKnowledgeBaseStore(
        name="nimbus",
        writable=False,
        max_search_results=2,
        filter={"equals": {"key": "topic", "value": "refund"}},
        config={"knowledge_base_id": kb, "knowledge_base_type": "VECTOR", "runtime_client": client},
    )
    if mock:
        with Stubber(client) as stub:
            stub.add_response(
                "retrieve",
                {
                    "retrievalResults": [
                        {
                            "content": {"text": "Approved refunds take 5 to 10 business days."},
                            "score": 0.9,
                            "location": {
                                "type": "S3",
                                "s3Location": {"uri": "s3://nimbus-demo/policies/refund.md"},
                            },
                            "metadata": {"topic": "refund"},
                        }
                    ]
                },
                {
                    "knowledgeBaseId": kb,
                    "retrievalQuery": {"text": "refund timing"},
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 2,
                            "filter": {"equals": {"key": "topic", "value": "refund"}},
                        }
                    },
                },
            )
            yield store
            stub.assert_no_pending_responses()
    else:
        yield store


def titan_vector(text: str, *, mock: bool) -> list[float]:
    client = aws_client("bedrock-runtime", mock=mock)
    request = {
        "modelId": course_value("BEDROCK_EMBEDDING_MODEL_ID"),
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({"inputText": text, "dimensions": 256, "normalize": True}),
    }
    if mock:
        payload = json.dumps({"embedding": [1.0] + [0.0] * 255, "inputTextTokenCount": 5}).encode()
        with Stubber(client) as stub:
            stub.add_response(
                "invoke_model",
                {
                    "body": StreamingBody(io.BytesIO(payload), len(payload)),
                    "contentType": "application/json",
                },
                request,
            )
            response = client.invoke_model(**request)
    else:
        response = client.invoke_model(**request)
    return json.loads(response["body"].read())["embedding"]


def bedrock_rerank(query: str, documents: list[str], *, mock: bool) -> list[dict]:
    client = aws_client("bedrock-agent-runtime", mock=mock)
    region = client.meta.region_name
    model = course_value("BEDROCK_RERANK_MODEL_ID")
    request = {
        "queries": [{"type": "TEXT", "textQuery": {"text": query}}],
        "sources": [
            {
                "type": "INLINE",
                "inlineDocumentSource": {"type": "TEXT", "textDocument": {"text": text}},
            }
            for text in documents
        ],
        "rerankingConfiguration": {
            "type": "BEDROCK_RERANKING_MODEL",
            "bedrockRerankingConfiguration": {
                "modelConfiguration": {
                    "modelArn": f"arn:aws:bedrock:{region}::foundation-model/{model}"
                },
                "numberOfResults": len(documents),
            },
        },
    }
    if mock:
        with Stubber(client) as stub:
            stub.add_response(
                "rerank",
                {
                    "results": [
                        {"index": i, "relevanceScore": 1 / (i + 1)} for i in range(len(documents))
                    ]
                },
                request,
            )
            return client.rerank(**request)["results"]
    return client.rerank(**request)["results"]
