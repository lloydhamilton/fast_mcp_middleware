import asyncio
import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TypeVar

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.dependencies import (
    get_access_token,
    get_http_headers,
    get_http_request,
)
from loguru import logger
from middleware.mcp_authentication import McpAuthentication
from pydantic import BaseModel, Field
from starlette.middleware import Middleware

load_dotenv()

logging.basicConfig(level=logging.INFO)
mcp = FastMCP("MCPDemo")


class Payload(BaseModel):
    """Payload for the test tool."""
    test: str = Field(..., description="Test payload for the tool.")


F = TypeVar("F", bound=Callable[..., Awaitable])


class AuthorisationError(Exception):
    """Custom exception for authentication errors."""

    pass


class authorise:
    def __init__(self, *, scope: str):
        self.required_scope = scope

    def __call__(self, func: F) -> F:
        """Decorator to check if the user has the required scope."""
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Callable: # ruff: noqa
            # grab the current request
            request = get_http_request()

            # pull the decoded token off of request.state
            decoded = getattr(request.state, "decoded_token", None)
            if decoded is None:
                raise AuthorisationError("HTTP 401 Unauthorised: no JWT token present")

            # extract the scopes claim (string or list)
            scopes_claim = (
                decoded.get("scope") or decoded.get("scopes") or decoded.get("scp")
            )
            if not scopes_claim:
                raise AuthorisationError(
                    "HTTP 401 Unauthorised: Not authorized to access this resource."
                )

            # normalize to a list
            if isinstance(scopes_claim, str):
                scopes: list[str] = scopes_claim.split()
            else:
                scopes = list(scopes_claim)

            # check for your required scope
            if self.required_scope not in scopes:
                raise AuthorisationError(
                    "HTTP 403 Forbidden: Not authorized to access this resource."
                )

            # all good!
            return await func(*args, **kwargs)

        return wrapper  # type: ignore


@mcp.tool()
@authorise(scope="fastmcp/read")
async def test(payload: Payload) -> str:
    logger.debug(f"Incoming payload: {payload}")
    logger.debug(get_http_request().headers)
    logger.debug(get_http_request().state.decoded_token)
    logger.debug(get_http_headers(include_all=True))
    logger.debug(f"Access token: {get_access_token()}")

    return payload.test


if __name__ == "__main__":
    import asyncio

    asyncio.run(mcp.run_http_async(middleware=[Middleware(McpAuthentication)]))
