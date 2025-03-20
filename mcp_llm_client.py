#!/usr/bin/env python3
# MCP LLM Client with HTTP/SSE transport

import asyncio
import os
import sys
import logging
from contextlib import AsyncExitStack
from typing import List, Dict, Any, Optional
import json

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCP-LLM-Client')


class MCPLLMClient:
    def __init__(self):
        """Initialize the MCP LLM client."""
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.openai = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.available_tools = []

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
        self.available_tools = response.tools
        logger.info(
            f"Connected to server with tools: {[tool.name for tool in self.available_tools]}")

        # List available resources
        resources = await self.session.list_resources()
        logger.info(
            f"Available resources: {[resource.name for resource in resources.resources]}")

        return self.available_tools, resources.resources

    async def process_query(self, query: str) -> str:
        """Process a query using GPT-4 and available tools."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        if not os.environ.get("OPENAI_API_KEY"):
            return "Error: OPENAI_API_KEY environment variable not set. Please create a .env file with your API key."

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that can use tools to help users accomplish tasks."
            },
            {
                "role": "user",
                "content": query
            }
        ]

        # Convert MCP tools to OpenAI tool format
        openai_tools = []
        for tool in self.available_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })

        # Initial GPT-4 API call
        logger.info("Sending query to GPT-4...")
        response = await self.openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )

        # Process response and handle tool calls
        final_text = []
        tool_calls = []

        message = response.choices[0].message
        final_text.append(message.content or "")

        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                logger.info(
                    f"GPT-4 is calling tool: {tool_name} with args: {tool_args}")

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                tool_calls.append(
                    {"name": tool_name, "args": tool_args, "result": result.content})

                # Add tool call and result to messages
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_args)
                            }
                        }
                    ]
                })
                messages.append({
                    "role": "tool",
                    "content": str(result.content),
                    "tool_call_id": tool_call.id
                })

            # If there were tool calls, get a final response from GPT-4
            if tool_calls:
                logger.info("Getting final response from GPT-4...")
                final_response = await self.openai.chat.completions.create(
                    model="gpt-4",
                    messages=messages
                )
                final_message = final_response.choices[0].message
                final_text.append(final_message.content or "")

        return "\n".join(text for text in final_text if text)

    async def interactive_mode(self):
        """Run an interactive session with GPT-4 and MCP tools."""
        print("\n=== Interactive MCP LLM Client with GPT-4 ===")
        print("Type your queries or 'exit' to quit")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "exit":
                    break

                response = await self.process_query(query)
                print("\nResponse:")
                print(response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error: {str(e)}")
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

    client = MCPLLMClient()
    try:
        await client.connect_to_server(server_url)
        await client.interactive_mode()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
