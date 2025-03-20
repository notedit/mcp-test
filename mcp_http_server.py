#!/usr/bin/env python3
# MCP Server using FastMCP (高级封装)

from mcp.server.fastmcp import FastMCP
import logging
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCP-FastMCP-Server')

# 尝试导入 FastMCP


# 创建 FastMCP 服务器实例
mcp = FastMCP("mcp-fastmcp-server", version="1.0.0")


@mcp.tool()
async def greet(name: str) -> str:
    """Greet a person by name."""
    logger.info(f"Greeting {name}")
    return f"Hello, {name}!"


@mcp.tool()
async def greet(name: str) -> str:
    """Greet a person by name."""
    logger.info(f"Greeting {name}")
    return f"Hello, {name}!"


@mcp.tool()
async def calculate(operation: str, a: float, b: float) -> float:
    """Perform a basic calculation.

    Args:
        operation: One of 'add', 'subtract', 'multiply', 'divide'
        a: First number
        b: Second number

    Returns:
        The result of the calculation
    """
    logger.info(f"Calculating {operation} with {a} and {b}")
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")


@mcp.resource("example://calculator")
async def calculator_resource() -> str:
    """Calculator resource."""
    return "Calculator Resource"


@mcp.resource("example://greeter")
async def greeter_resource() -> str:
    """Greeter resource."""
    return "Greeter Resource"


def main():
    """启动 FastMCP 服务器"""
    logger.info("Starting MCP FastMCP server on http://localhost:8000")
    # 获取 FastAPI 应用并运行

    mcp.run('sse')


if __name__ == "__main__":
    main()
