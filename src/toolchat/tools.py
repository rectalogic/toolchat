# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later
import os

import yaml
from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio


def load_mcp_servers(path: str | None, enable_tool_server: list[str] | None) -> list[MCPServer]:
    if not path or not os.path.exists(path):
        return []
    with open(path) as f:
        tool_servers = yaml.safe_load(f)["mcpServers"]
        if enable_tool_server is None:
            return [_load_mcp_server(s) for s in tool_servers.values()]
        else:
            return [_load_mcp_server(s) for name, s in tool_servers.items() if name in enable_tool_server]


def _load_mcp_server(d: dict) -> MCPServer:
    match d.pop("type", "stdio"):
        case "stdio":
            return MCPServerStdio(**d)
        case "http":
            return MCPServerHTTP(**d)
        case x:
            raise RuntimeError(f"Invalid MCPServer type {x}")
