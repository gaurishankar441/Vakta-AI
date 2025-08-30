from app.middlewares.ws_token_header import TokenQueryToAuthHeader
from fastapi import FastAPI
from app.routers import health, metrics, auth, chat, ws_audio, echo, auth_otp

# Build the real FastAPI app
fastapi_app = FastAPI(title="vakta-api", version="0.0.1")

# Routers
fastapi_app.include_router(health.router, prefix="/api")
fastapi_app.include_router(metrics.router, prefix="/api")
fastapi_app.include_router(auth.router)
fastapi_app.include_router(chat.router)
fastapi_app.include_router(ws_audio.router)
fastapi_app.include_router(echo.router)
fastapi_app.include_router(auth_otp.router)

# --- OpenTelemetry (optional) ---
try:
    from app.otel_init import setup_tracing
    setup_tracing(fastapi_app)
except Exception as e:
    print("[otel] init skipped:", e)

# --- Prometheus metrics (exposed at /api/metrics) ---
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(fastapi_app).expose(fastapi_app, endpoint="/api/metrics")
except Exception as e:
    import logging
    logging.getLogger(__name__).warning("metrics disabled: %s", e)

# Wrap WITH the token-header middleware LAST so .include_router was called on the FastAPI app
app = TokenQueryToAuthHeader(fastapi_app)
print("[mw] TokenQueryToAuthHeader ACTIVE")
