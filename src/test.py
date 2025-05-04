import logging

import requests
from fastmcp.client import Client
from fastmcp.client.transports import SSETransport
from loguru import logger

logging.basicConfig(level=logging.DEBUG)

async def main():
    response = requests.post(
        'https://hypergent.auth.eu-west-1.amazoncognito.com/oauth2/token',
        data="grant_type=client_credentials&client_id=7c8li2itj8kjof3s8t0tapmjje&client_secret=18vhmqne6bbaedafknho15d584f4tv67stg120o7hf1ljiqknt64&scope=fastmcp/read",
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
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
    #
    # async with sse_client("http://127.0.0.1:8080/sse") as (read, write):
    #     async with ClientSession(read, write) as session:
    #         await session.initialize()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
