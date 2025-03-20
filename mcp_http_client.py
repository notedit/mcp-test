#!/usr/bin/env python3
# MCP Client using HTTP/SSE transport

import asyncio
import sys
import logging
from contextlib import AsyncExitStack

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCP-HTTP-Client')


class MCPHTTPClient:
    def __init__(self):
        """Initialize the MCP HTTP/SSE client."""
        self.session = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_url: str):
        """Connect to an MCP HTTP/SSE server.

        Args:
            server_url: URL of the MCP server (e.g., http://localhost:8000)
        """
        logger.info(f"Connecting to MCP server at {server_url}")

        # Create HTTP/SSE client
        transport = await self.exit_stack.enter_async_context(sse_client(server_url))
        read, write = transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))

        # Initialize the session
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        logger.info(
            f"Connected to server with tools: {[tool.name for tool in tools]}")

        # List available resources
        resources = await self.session.list_resources()
        logger.info(
            f"Available resources: {[resource.name for resource in resources.resources]}")

        return tools, resources.resources

    async def call_greet(self, name: str):
        """Call the greet tool."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        logger.info(f"Calling greet tool with name: {name}")
        result = await self.session.call_tool("greet", {"name": name})
        return result.content

    async def call_calculate(self, operation: str, a: float, b: float):
        """Call the calculate tool."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        logger.info(
            f"Calling calculate tool with operation: {operation}, a: {a}, b: {b}")
        result = await self.session.call_tool(
            "calculate",
            {"operation": operation, "a": a, "b": b}
        )
        return result.content

    async def interactive_mode(self):
        """Run an interactive session with the MCP server."""
        print("\n=== Interactive MCP HTTP/SSE Client ===")
        print("Available commands:")
        print("  greet <name> - Greet a person")
        print("  calc <operation> <a> <b> - Perform a calculation")
        print("  exit - Exit the client")

        while True:
            try:
                command = input("\n> ").strip()

                if command.lower() == "exit":
                    break

                parts = command.split()
                if not parts:
                    continue

                if parts[0] == "greet":
                    if len(parts) < 2:
                        print("Usage: greet <name>")
                        continue
                    name = " ".join(parts[1:])
                    result = await self.call_greet(name)
                    print(f"Result: {result}")

                elif parts[0] == "calc":
                    if len(parts) != 4:
                        print("Usage: calc <operation> <a> <b>")
                        print("Operations: add, subtract, multiply, divide")
                        continue

                    operation = parts[1]
                    try:
                        a = float(parts[2])
                        b = float(parts[3])
                    except ValueError:
                        print("Error: a and b must be numbers")
                        continue

                    try:
                        result = await self.call_calculate(operation, a, b)
                        print(f"Result: {result}")
                    except Exception as e:
                        print(f"Error: {str(e)}")

                else:
                    print(f"Unknown command: {parts[0]}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {str(e)}")

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        server_url = "http://localhost:8000/sse"
        print(f"No server URL provided, using default: {server_url}")
    else:
        server_url = sys.argv[1]

    client = MCPHTTPClient()
    try:
        await client.connect_to_server(server_url)
        await client.interactive_mode()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
