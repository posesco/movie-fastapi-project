from prometheus_client import Counter, Histogram


class CustomMetrics:
    def __init__(self):
        self.requests_total = Counter(
            "app_requests_total", "Total number of requests by endpoint"
        )

        self.request_duration = Histogram(
            "app_request_duration_seconds", "Request duration in seconds"
        )

    def init(self):
        pass


custom_metrics = CustomMetrics()
