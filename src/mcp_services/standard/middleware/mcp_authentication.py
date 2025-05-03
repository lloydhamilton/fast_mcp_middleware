import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

log = logging.getLogger(__name__)


class McpAuthentication(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if "Authorization" not in request.headers:
            response = Response(status_code=401)
            return response
        # response = await call_next(request)
        return await call_next(request)

    # async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
    #     if scope["type"] not in ["http"]:
    #         await self.app(scope, receive, send)
    #         return
    #     log.info("Incoming request to %s", scope["path"])
    #     log.info("Incoming headers %s", scope["headers"])
    #     conn = HTTPConnection(scope)
    #     if "Authorisation" not in conn.headers:
    #         raise ValueError(f"Missing Authorization header: {conn.headers}")
    #     return await self.app(scope, receive, send)
