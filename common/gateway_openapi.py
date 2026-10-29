"""Validate a real CreateGatewayTarget request without creating a resource."""

import json
import re
from urllib.parse import urlsplit

from botocore.session import get_session
from botocore.validate import validate_parameters


def openapi_target(settings, gateway_id, api_url):
    url = urlsplit(api_url)
    host = r"[a-z0-9]+\.execute-api\." + re.escape(settings.aws_region) + r"\.amazonaws\.com"
    if (
        url.scheme != "https"
        or not re.fullmatch(host, url.hostname or "")
        or url.username
        or url.password
        or url.query
        or url.fragment
        or url.port
    ):
        raise ValueError(
            "Use a reviewed regional API Gateway HTTPS endpoint with IAM authorization"
        )
    schema = {
        "openapi": "3.0.3",
        "info": {"title": "Nimbus public booking API", "version": "1.0"},
        "servers": [{"url": api_url}],
        "paths": {
            "/flights": {
                "get": {
                    "operationId": "searchFlights",
                    "description": "Search public synthetic flight quotes",
                    "parameters": [
                        {
                            "name": "destination",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Public quotes",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "flight_id": {"type": "string"},
                                                "price_usd": {"type": "string"},
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            }
        },
    }
    request = {
        "gatewayIdentifier": gateway_id,
        "name": "nimbusRest",
        "targetConfiguration": {"mcp": {"openApiSchema": {"inlinePayload": json.dumps(schema)}}},
        "credentialProviderConfigurations": [
            {
                "credentialProviderType": "GATEWAY_IAM_ROLE",
                "credentialProvider": {
                    "iamCredentialProvider": {
                        "service": "execute-api",
                        "region": settings.aws_region,
                    }
                },
            }
        ],
    }
    validate_parameters(
        request,
        get_session()
        .get_service_model("bedrock-agentcore-control")
        .operation_model("CreateGatewayTarget")
        .input_shape,
    )
    return request
