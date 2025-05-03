import asyncio
import logging

from dotenv import load_dotenv
from fastmcp import FastMCP
from loguru import logger
from mcp.server.sse import SseServerTransport
from middleware.mcp_authentication import McpAuthentication
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.routing import Mount, Route

load_dotenv()

logging.basicConfig(level=logging.DEBUG)


class AuthenticatedFastMCP(FastMCP):
    def sse_app(self) -> Starlette:
        """Return an instance of the SSE server app."""
        sse = SseServerTransport(self.settings.message_path)

        async def handle_sse(request: Request) -> None:
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # type: ignore[reportPrivateUsage]
            ) as streams:
                await self._mcp_server.run(
                    streams[0],
                    streams[1],
                    self._mcp_server.create_initialization_options(),
                )

        return Starlette(
            debug=self.settings.debug,
            routes=[
                Route(self.settings.sse_path, endpoint=handle_sse),
                Mount(self.settings.message_path, app=sse.handle_post_message),
            ],
            middleware=[Middleware(McpAuthentication)],
        )


mcp = AuthenticatedFastMCP("ObligationRegisterExport")


class Payload(BaseModel):
    test: str = Field(..., description="Test payload for the tool.")


@mcp.tool()
async def test(payload: Payload) -> str:
    """Receives obligation register data and uploads it to S3."""
    logger.debug(f"Incoming payload: {payload}")
    return payload.test


if __name__ == "__main__":
    asyncio.run(mcp.run_async(transport="sse"))
