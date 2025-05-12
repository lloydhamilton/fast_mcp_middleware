import logging
import os

import requests
from dotenv import load_dotenv
from fastmcp.client import Client
from fastmcp.client.transports import SSETransport
from loguru import logger

logging.basicConfig(level=logging.DEBUG)
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

CLIENT_ID = os.getenv("USER_POOL_CLIENT_ID")
CLIENT_SECRET = os.getenv("USER_POOL_CLIENT_SECRET")


async def main() -> None:
    """Main function to test the authenticated FastMCP client."""
    response = requests.post(
        "https://hypergent.auth.eu-west-1.amazoncognito.com/oauth2/token",
        data=f"grant_type=client_credentials&"
        f"client_id={CLIENT_ID}&"
        f"client_secret={CLIENT_SECRET}&"
        f"scope=fastmcp/read",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    transport = SSETransport(
        url="http://127.0.0.1:8000/sse",
        headers={
            "Authorization": f"Bearer {response.json()['access_token']}",
            "x-test": "test",
        },
    )
    async with Client(transport) as client:
        # Call a tool
        result = await client.call_tool(
            "test", arguments={"payload": {"test": "value"}}
        )
        logger.info(f"Tool result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
