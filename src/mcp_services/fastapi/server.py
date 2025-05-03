import logging

from fastapi import FastAPI
from fastmcp import FastMCP
from middleware.mcp_authentication import McpAuthentication
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.DEBUG)
# Your existing FastAPI application
fastapi_app = FastAPI(title="My Existing API")
fastapi_app.add_middleware(McpAuthentication)


class Payload(BaseModel):
    payload: str = Field(..., description="Test payload for the tool.")


@fastapi_app.get("/status")
def get_status():
    return {"status": "running"}


@fastapi_app.post("/items", operation_id="get_items")
def create_item(payload: Payload):
    return payload.test_payload


# Generate an MCP server directly from the FastAPI app
mcp = FastMCP.from_fastapi(fastapi_app)

if __name__ == "__main__":
    mcp.run(transport="sse")
