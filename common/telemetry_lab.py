"""Export actual Strands spans through a strict public-metrics projection.

Run in a fresh process: OpenTelemetry providers and the Strands tracer are process globals.
"""

import argparse
import asyncio
import json
import os
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread


@contextmanager
def local_otlp_receiver():
    """A real OTLP/HTTP receiving fixture; Jaeger is an optional external viewer."""
    received = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
                ExportTraceServiceRequest,
            )

            data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            request = ExportTraceServiceRequest.FromString(data)
            received.append(request)
            self.send_response(200)
            self.send_header("Content-Type", "application/x-protobuf")
            self.end_headers()
            self.wfile.write(b"")

        def log_message(self, *_):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1/traces", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def trace_run(settings, *, endpoint=None, cloud=False):
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
    from opentelemetry.sdk.trace.export import (
        ConsoleSpanExporter,
        SimpleSpanProcessor,
        SpanExporter,
    )
    from opentelemetry.trace import Status
    from strands.telemetry import StrandsTelemetry

    from common.production_support import answer_support

    os.environ["OTEL_SDK_DISABLED"] = "false"
    os.environ["OTEL_SEMCONV_STABILITY_OPT_IN"] = "gen_ai_unredacted_attributes="
    provider = TracerProvider(resource=Resource({"service.name": "nimbus-support"}))
    delegates = [ConsoleSpanExporter()]
    if endpoint:
        delegates.append(OTLPSpanExporter(endpoint=endpoint, timeout=5))
    if cloud:
        from common.aws_otlp import AWSOTLPExporter

        delegates.append(AWSOTLPExporter(settings))
    count = []
    failures = []

    class PublicExporter(SpanExporter):
        def export(self, spans):
            from opentelemetry.sdk.trace.export import SpanExportResult

            clean = []
            for span in spans:
                # Drop arbitrary attributes, events, links, status prose and dynamic names.
                attributes = {
                    k: v
                    for k, v in span.attributes.items()
                    if k.startswith("gen_ai.usage.") and type(v) in (int, float)
                }
                clean.append(
                    ReadableSpan(
                        name="nimbus.operation",
                        context=span.context,
                        parent=span.parent,
                        kind=span.kind,
                        start_time=span.start_time,
                        end_time=span.end_time,
                        status=Status(span.status.status_code),
                        attributes=attributes,
                        events=[],
                        links=[],
                        resource=provider.resource,
                    )
                )
            count.extend(clean)
            try:
                outcomes = [exporter.export(clean) for exporter in delegates]
            except Exception:
                failures.append("export failed")
                return SpanExportResult.FAILURE
            if any(r != SpanExportResult.SUCCESS for r in outcomes):
                failures.append("export failed")
                return SpanExportResult.FAILURE
            return SpanExportResult.SUCCESS

        def shutdown(self):
            for exporter in delegates:
                exporter.shutdown()

    provider.add_span_processor(SimpleSpanProcessor(PublicExporter()))
    StrandsTelemetry(tracer_provider=provider)
    # Explicitly establish the provider before constructing the first Agent/tracer in this process.
    from opentelemetry import trace

    trace.set_tracer_provider(provider)
    try:
        result = asyncio.run(
            answer_support({"prompt": "Refund time? PRIVATE-MARKER-DO-NOT-EXPORT"}, settings)
        )
    finally:
        provider.force_flush(timeout_millis=5000)
        provider.shutdown()
    if failures:
        raise RuntimeError("Trace export failed; check the local collector endpoint")
    if not count:
        raise RuntimeError("No spans captured; run the tracing lesson in a fresh process")
    return {"spans": len(count), "usage": result["usage"], "projection": "numeric usage only"}


def main():
    from common.config import load_settings
    from common.network import offline_network

    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--otlp", help="Reviewed local collector URL, ending /v1/traces")
    parser.add_argument(
        "--cloud", action="store_true", help="Explicitly export to AWS X-Ray OTLP; billable"
    )
    args = parser.parse_args()
    if args.cloud and args.mock:
        parser.error(
            "Cloud export requires live credentials; omit --mock only after reviewing costs"
        )
    if args.otlp:
        from urllib.parse import urlsplit

        target = urlsplit(args.otlp)
        if target.scheme != "http" or target.hostname not in {"localhost", "127.0.0.1"}:
            parser.error("This lesson exports only to a local HTTP collector")
    cfg = load_settings(provider="mock" if args.mock else None)
    if args.mock:
        with offline_network(), local_otlp_receiver() as (endpoint, received):
            result = trace_run(cfg, endpoint=args.otlp or endpoint)
            if not args.otlp:
                assert received and "PRIVATE-MARKER" not in str(received)
                result["otlp_batches_received"] = len(received)
    else:
        result = trace_run(cfg, endpoint=args.otlp, cloud=args.cloud)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
