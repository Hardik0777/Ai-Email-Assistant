"""Prometheus metrics, exposed at /metrics."""
from prometheus_client import Counter, Histogram

REQUESTS = Counter("http_requests_total", "HTTP requests", ["method", "path", "status"])
LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["path"])
AI_RESULTS = Counter("ai_results_total", "Email action results by source", ["action", "source"])
CACHE = Counter("cache_lookups_total", "AI response cache lookups", ["result"])
RATE_LIMITED = Counter("rate_limited_total", "Requests rejected by the rate limiter")
