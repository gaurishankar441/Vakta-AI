from __future__ import annotations
import os
from typing import Any, Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# instrumentations
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.starlette import StarletteInstrumentor
try:
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
except Exception:
    Psycopg2Instrumentor = None
try:
    from opentelemetry.instrumentation.redis import RedisInstrumentor
except Exception:
    RedisInstrumentor = None
try:
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
except Exception:
    RequestsInstrumentor = None
try:
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
except Exception:
    HTTPXClientInstrumentor = None

def _setup_provider() -> None:
    svc = os.getenv("OTEL_SERVICE_NAME", "vakta-api")
    res_attrs = os.getenv("OTEL_RESOURCE_ATTRIBUTES", "")
    attrs = {}
    for kv in filter(None, (x.strip() for x in res_attrs.split(","))):
        if "=" in kv:
            k, v = kv.split("=", 1)
            attrs[k.strip()] = v.strip()

    provider = TracerProvider(resource=Resource.create({"service.name": svc, **attrs}))
    exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4317"), insecure=True)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

def setup_tracing(app) -> None:
    """Call once during startup with your FastAPI app object."""
    if not isinstance(trace.get_tracer_provider(), TracerProvider):
        _setup_provider()

    # Web framework
    FastAPIInstrumentor.instrument_app(app)
    StarletteInstrumentor().instrument()

    # DB / cache / HTTP
    if Psycopg2Instrumentor:
        Psycopg2Instrumentor().instrument()
    if RedisInstrumentor:
        RedisInstrumentor().instrument()
    if RequestsInstrumentor:
        RequestsInstrumentor().instrument()
    if HTTPXClientInstrumentor:
        HTTPXClientInstrumentor().instrument()

def ws_span(name: str = "ws.session"):
    """Context manager to trace a websocket session; use inside your WS handler."""
    tracer = trace.get_tracer("vakta.ws")
    return tracer.start_as_current_span(name)
