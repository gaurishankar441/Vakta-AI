from prometheus_client import Counter, Histogram

# Total messages by role
chat_messages_total = Counter(
    "chat_messages_total",
    "Total chat messages by role",
    ["role"],
)

# Latency of the chat handler
chat_request_latency_seconds = Histogram(
    "chat_request_latency_seconds",
    "Latency of /api/v1/chat/message handler in seconds",
)
