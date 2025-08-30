from urllib.parse import parse_qs

class TokenQueryToAuthHeader:
    """Inject Authorization: Bearer <token> from ?token= for WebSocket handshakes."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "websocket":
            raw_qs = scope.get("query_string", b"") or b""
            qs = parse_qs(raw_qs.decode("latin1"))
            token_list = qs.get("token") or qs.get("Token")
            if token_list:
                token = token_list[0]
                print(f"[mw] injecting Authorization (query token len={len(token)})")
                headers, seen = [], False
                for k, v in scope.get("headers", []):
                    if k.lower() == b"authorization":
                        headers.append((b"authorization", f"Bearer {token}".encode("latin1"))); seen=True
                    else:
                        headers.append((k, v))
                if not seen:
                    headers.append((b"authorization", f"Bearer {token}".encode("latin1")))
                scope = dict(scope); scope["headers"] = tuple(headers)
        await self.app(scope, receive, send)
