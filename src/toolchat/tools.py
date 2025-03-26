# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later
import typing as t
import os

import yaml
from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio
from pydantic_ai.tools import ToolDefinition

class MCPServerStdioSchema(MCPServerStdio):
    @t.override
    async def list_tools(self) -> list[ToolDefinition]:
        return [modify_schema(tool) for tool in await super().list_tools()]

class MCPServerHTTPSchema(MCPServerHTTP):
    @t.override
    async def list_tools(self) -> list[ToolDefinition]:
        return [modify_schema(tool) for tool in await super().list_tools()]

def modify_schema(tool: ToolDefinition) -> ToolDefinition:
    tool.parameters_json_schema.pop("$schema", None)
    return tool


def load_mcp_servers(path: str) -> list[MCPServer]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [_load_mcp_server(s) for s in yaml.safe_load(f)]


def _load_mcp_server(d: dict) -> MCPServer:
    server = d.get("server")
    if not server:
        raise RuntimeError(f"Missing MCPServer definition {d}")
    match d.get("type"):
        case "stdio":
            return MCPServerStdioSchema(**server)
        case "http":
            return MCPServerHTTPSchema(**server)
        case x:
            raise RuntimeError(f"Invalid MCPServer type {x}")
