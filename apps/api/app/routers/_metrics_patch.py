from prometheus_client import Counter, Gauge, Histogram
from time import perf_counter

# Counters with extra "status" label
chat_messages_total = Counter(
    "chat_messages_total",
    "Total chat messages by role & status",
    ["role", "status"],
)

# Gauge for in-flight requests
chat_in_flight = Gauge(
    "chat_requests_in_flight",
    "Number of in-flight /chat requests"
)

# Histogram for latency
chat_latency = Histogram(
    "chat_request_latency_seconds",
    "Latency of /api/v1/chat/message handler in seconds",
    buckets=(0.005,0.01,0.025,0.05,0.1,0.25,0.5,1,2.5,5,10,float("inf")),
)
