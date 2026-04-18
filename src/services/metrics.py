from opentelemetry import metrics

class CustomMetrics:
    def __init__(self):
        self.meter = metrics.get_meter("fastapi-app")
        
        self.requests_total = self.meter.create_counter(
            "app_requests_total",
            description="Total number of requests by endpoint",
            unit="1"
        )

        self.request_duration = self.meter.create_histogram(
            "app_request_duration_seconds",
            description="Request duration in seconds",
            unit="s"
        )

    def init(self):
        # La inicialización de OTel se maneja en main.py
        pass


custom_metrics = CustomMetrics()
