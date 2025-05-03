import asyncio

from dotenv import load_dotenv
from fastmcp import FastMCP
from loguru import logger
from pydantic import BaseModel, Field

load_dotenv()

mcp = FastMCP("ObligationRegisterExport")

class Payload(BaseModel):
    test_payload: str = Field(..., description="Test payload for the tool.")

@mcp.tool()
async def export_register_tool(payload: Payload) -> str:
    """Receives obligation register data and uploads it to S3."""
    logger.debug(f"Incoming payload: {payload}")
    return payload.test_payload


if __name__ == "__main__":
    asyncio.run(mcp.run_async(transport="sse"))
