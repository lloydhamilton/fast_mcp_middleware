import logging

from fastmcp.client import Client
from fastmcp.client.transports import SSETransport
from loguru import logger

logging.basicConfig(level=logging.DEBUG)


async def main():
    transport = SSETransport(
        url="http://127.0.0.1:8000/sse",
        headers={"Authorizdfation": "Bearer this is a test", "x-test": "test"},
    )
    async with Client(transport) as client:
        # Call a tool
        result = await client.call_tool(
            "test", arguments={"payload": {"test": "value"}}
        )
        logger.info(f"Tool result: {result}")
    #
    # async with sse_client("http://127.0.0.1:8080/sse") as (read, write):
    #     async with ClientSession(read, write) as session:
    #         await session.initialize()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
