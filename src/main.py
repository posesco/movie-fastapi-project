from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import socket

from .core.database import init_db
from .core.config import settings, tags_metadata
from .middlewares.error_handler import ErrorHandler
from .services.metrics import custom_metrics
from opentelemetry import metrics, trace, _logs
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import logging

from .api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    otel_collector_endpoint = "http://alloy:4317"

    # Setup Tracing
    trace_exporter = OTLPSpanExporter(endpoint=otel_collector_endpoint, insecure=True)
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(trace_exporter))

    # Setup Metrics
    metric_exporter = OTLPMetricExporter(endpoint=otel_collector_endpoint, insecure=True)
    reader = PeriodicExportingMetricReader(metric_exporter)
    metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

    # Setup Logging
    log_exporter = OTLPLogExporter(endpoint=otel_collector_endpoint, insecure=True)
    logger_provider = LoggerProvider()
    _logs.set_logger_provider(logger_provider)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    # Attach OTel handler to standard logging
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    await init_db()
    yield


app = FastAPI(
    title=settings.project_title,
    version=settings.project_version,
    description=settings.project_desc,
    debug=settings.project_debug_mode,
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
custom_metrics.init()
app.add_middleware(ErrorHandler)
app.include_router(api_router, prefix="/api/v1")

start_time = datetime.now(timezone.utc)


@app.get("/", tags=["health"], status_code=status.HTTP_302_FOUND)
async def redirect_to_status() -> RedirectResponse:
    return RedirectResponse(url="/_status/", status_code=status.HTTP_302_FOUND)


@app.get("/_status/", tags=["health"], status_code=200)
async def _status() -> dict:
    from sqlmodel import select
    from .core.database import engine

    db_status = "OK"
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
    except Exception as e:
        db_status = f"Error: {str(e)}"

    current_time = datetime.now(timezone.utc)
    uptime = current_time - start_time
    return JSONResponse(
        status_code=200,
        content={
            "status": "Live",
            "version": app.version,
            "db_status": db_status,
            "uptime": str(uptime),
            "server": socket.gethostname(),
        },
    )


@app.get("/health-check/", tags=["health"], status_code=200)
async def health_check() -> bool:
    return True
