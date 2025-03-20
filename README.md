# MCP (Model Context Protocol) Implementation

This project provides implementations of MCP (Model Context Protocol) servers and clients in Python.

## Overview

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. This project includes:

1. A basic socket-based implementation (for learning purposes)
2. An official MCP SDK implementation with HTTP/SSE transport
3. LLM integration example using Claude with HTTP/SSE transport
4. FastMCP implementation - a higher-level wrapper for easier MCP server creation

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

### 快速安装（推荐）

使用提供的安装脚本快速设置环境：

```bash
./setup.sh
```

这个脚本会自动：
1. 创建虚拟环境
2. 安装所有依赖
3. 创建 `.env` 文件（如果不存在）
4. 使所有 Python 文件可执行

### 手动安装

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. For LLM integration, copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API key
   ```

## Basic Socket Implementation

This is a simple implementation using sockets and JSON for educational purposes.

### Starting the Basic Server

```bash
python mcp_server.py
```

### Using the Basic Client

```bash
python mcp_client.py [host] [port]
```

## Official MCP SDK Implementation (HTTP/SSE)

This implementation uses the official MCP Python SDK with HTTP/SSE transport.

### Starting the MCP HTTP/SSE Server

```bash
python mcp_http_server.py
```

The server will start on http://localhost:8000.

### Using the MCP HTTP/SSE Client

```bash
python mcp_http_client.py [server_url]
```

If no server URL is provided, it will default to http://localhost:8000.

## FastMCP Implementation

The server now uses FastMCP, a higher-level wrapper around the MCP SDK that provides a more concise API for creating MCP servers.

### Key Features of FastMCP

- Simplified tool and resource registration with decorators
- Automatic type handling and validation
- Streamlined API for creating MCP servers

### Starting the FastMCP Server

```bash
python mcp_http_server.py
```

The server will start on http://localhost:8000 and is fully compatible with the existing clients.

## LLM Integration with Claude

This example shows how to use MCP with Claude to create an AI assistant that can use tools.

### Running the MCP LLM Client

```bash
python mcp_llm_client.py [server_url]
```

If no server URL is provided, it will default to http://localhost:8000.

## Available Tools

The MCP server provides the following tools:

1. **greet** - Greets a person by name
2. **calculate** - Performs basic calculations (add, subtract, multiply, divide)

## Protocol

The official MCP protocol is used in the SDK implementation. For more information, visit [modelcontextprotocol.io](https://modelcontextprotocol.io).

## Transport Layers

This project demonstrates different transport layers for MCP:

1. **Socket-based** - A custom implementation using TCP sockets (for learning)
2. **HTTP/SSE** - HTTP-based transport with Server-Sent Events for network communication

## Extending the Implementation

You can extend the MCP server by:

1. Adding more tools to the server implementations
2. Implementing additional resources
3. Creating specialized servers for specific use cases
4. Implementing other transport layers (WebSockets, gRPC, etc.)

## Troubleshooting

### 导入错误

如果遇到 `ImportError: cannot import name 'http_client'` 或类似错误，可能是 MCP 库的版本问题。在新版本的 MCP 中，`http_client` 可能已经被替换为 `sse_client`。本项目已经添加了兼容性代码，尝试多种导入路径。如果仍然遇到问题，请尝试：

```bash
pip install --upgrade mcp
```

### API 密钥问题

使用 LLM 客户端时，确保已经在 `.env` 文件中设置了正确的 Anthropic API 密钥：

```
ANTHROPIC_API_KEY=your_api_key_here
```

## Resources

- [MCP Official Documentation](https://modelcontextprotocol.io)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)
- [Anthropic Claude Documentation](https://docs.anthropic.com)

## License

This project is open source and available under the MIT License.
