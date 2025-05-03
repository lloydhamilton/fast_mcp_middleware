# server.py
from mcpengine import MCPEngine

mcp = MCPEngine("Demo")


@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    return f"Hello, {name}!"
