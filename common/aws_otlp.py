"""SigV4-authenticated OTLP/HTTP export using short-lived AWS role credentials."""

import httpx
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from google.protobuf.message import DecodeError
from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceResponse
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from common.cloud_clients import session


class AWSOTLPExporter(SpanExporter):
    def __init__(self, settings, *, transport=None):
        self.settings = settings
        self.session = session(settings)
        self.http = httpx.Client(
            timeout=10, follow_redirects=False, trust_env=False, transport=transport
        )

    def export(self, spans):
        body = encode_spans(spans).SerializeToString()
        endpoint = f"https://xray.{self.settings.aws_region}.amazonaws.com/v1/traces"
        request = AWSRequest(
            method="POST",
            url=endpoint,
            data=body,
            headers={"Content-Type": "application/x-protobuf"},
        )
        # Refresh role/SSO credentials for each batch; never store them in model context.
        credentials = self.session.get_credentials().get_frozen_credentials()
        SigV4Auth(credentials, "xray", self.settings.aws_region).add_auth(request)
        try:
            response = self.http.post(endpoint, content=body, headers=dict(request.headers))
            if not response.is_success:
                return SpanExportResult.FAILURE
            result = ExportTraceServiceResponse.FromString(response.content)
            return (
                SpanExportResult.FAILURE
                if result.partial_success.rejected_spans
                else SpanExportResult.SUCCESS
            )
        except (httpx.HTTPError, DecodeError):
            return SpanExportResult.FAILURE

    def shutdown(self):
        self.http.close()
