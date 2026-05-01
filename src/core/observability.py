import logging
from opentelemetry import metrics, trace, _logs
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI

from .config import settings

logger = logging.getLogger(__name__)

def setup_observability(app: FastAPI) -> None:
    if not settings.otel_enabled:
        logger.info("OpenTelemetry is disabled.")
        return

    resource = Resource.create({"service.name": settings.otel_service_name})

    # Setup Tracing
    trace_exporter = OTLPSpanExporter(endpoint=settings.otel_collector_endpoint, insecure=True)
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    # Setup Metrics
    metric_exporter = OTLPMetricExporter(endpoint=settings.otel_collector_endpoint, insecure=True)
    reader = PeriodicExportingMetricReader(metric_exporter)
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)

    # Setup Logging
    log_exporter = OTLPLogExporter(endpoint=settings.otel_collector_endpoint, insecure=True)
    logger_provider = LoggerProvider(resource=resource)
    _logs.set_logger_provider(logger_provider)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    # Attach OTel handler to root logging
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    logger.info("OpenTelemetry initialized successfully for service: %s", settings.otel_service_name)
